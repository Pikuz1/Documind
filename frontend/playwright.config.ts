import { existsSync } from 'node:fs'
import path from 'node:path'
import { defineConfig, devices } from '@playwright/test'

// Own ports, so a dev server you have running (maybe in real-AI mode) is never reused.
const API_PORT = 8001
const WEB_PORT = 5174

const backendDir = path.resolve(import.meta.dirname, '../backend')
const venvPython = path.join(
  backendDir,
  '.venv',
  process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
)
// Locally use the project venv; CI installs the backend deps into its default python.
const python = existsSync(venvPython) ? `"${venvPython}"` : 'python'

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  workers: 1, // the tests share one backend, so they run one after another
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: { baseURL: `http://localhost:${WEB_PORT}`, trace: 'on-first-retry' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      // Wipe the previous run's data (in Python, so it works on Windows too), then start the API.
      command:
        `${python} -c "import shutil; shutil.rmtree('.e2e-data', ignore_errors=True)"` +
        ` && ${python} -m uvicorn app.main:app --port ${API_PORT}`,
      cwd: backendDir,
      url: `http://localhost:${API_PORT}/api/health`,
      // Fake embeddings give arbitrary relevance scores, so let every chunk through.
      env: { AI_PROVIDER: 'fake', DATA_DIR: '.e2e-data', MIN_RELEVANCE_SCORE: '-1' },
      reuseExistingServer: false,
    },
    {
      command: `npm run dev -- --port ${WEB_PORT} --strictPort`,
      url: `http://localhost:${WEB_PORT}`,
      env: { API_PROXY_TARGET: `http://localhost:${API_PORT}` },
      reuseExistingServer: false,
    },
  ],
})
