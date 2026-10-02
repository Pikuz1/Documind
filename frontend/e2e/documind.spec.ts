import { readFileSync } from 'node:fs'
import path from 'node:path'
import { expect, test, type Page } from '@playwright/test'

const FIXTURES = path.join(import.meta.dirname, 'fixtures')
// What the backend's fake LLM always answers (FAKE_ANSWER in app/ai/providers.py).
const FAKE_ANSWER = 'According to the document, the notice period is three months (p. 1).'

/** Uploads a fixture under a test-specific name, so tests sharing one backend never collide. */
async function upload(page: Page, fixture: string, name: string) {
  await page.getByTestId('upload-input').setInputFiles({
    name,
    mimeType: 'application/pdf',
    buffer: readFileSync(path.join(FIXTURES, fixture)),
  })
}

function documentItem(page: Page, name: string) {
  return page.getByRole('list', { name: 'Documents' }).getByRole('listitem').filter({ hasText: name })
}

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1, name: 'DocuMind' })).toBeVisible()
})

test('uploads a contract and answers a question with sources', async ({ page }) => {
  await upload(page, 'sample_contract.pdf', 'ask-flow.pdf')

  await expect(documentItem(page, 'ask-flow.pdf')).toBeVisible()
  await expect(page.getByRole('heading', { level: 2, name: 'ask-flow.pdf' })).toBeVisible()

  await page.getByTestId('question-input').fill('What is the notice period?')
  await page.getByTestId('ask-button').click()

  const answerCard = page.getByTestId('answer-card')
  await expect(answerCard).toContainText(FAKE_ANSWER)
  await expect(page.getByTestId('source-item').first()).toBeVisible()
})

test('shows an error for a PDF without text', async ({ page }) => {
  await upload(page, 'empty.pdf', 'scanned-flow.pdf')

  await expect(page.getByRole('alert')).toContainText('no extractable text')
  await expect(documentItem(page, 'scanned-flow.pdf')).toHaveCount(0)
})

test('deletes a document', async ({ page }) => {
  await upload(page, 'sample_contract.pdf', 'delete-flow.pdf')
  await expect(documentItem(page, 'delete-flow.pdf')).toBeVisible()

  await page.getByRole('button', { name: 'Delete delete-flow.pdf' }).click()

  await expect(documentItem(page, 'delete-flow.pdf')).toHaveCount(0)
  await page.reload() // deleted on the server too, not just in the UI
  // Wait for the reloaded list, or "count 0" would pass before it even arrives.
  await expect(page.getByText('Loading documents…')).toHaveCount(0)
  await expect(documentItem(page, 'delete-flow.pdf')).toHaveCount(0)
})
