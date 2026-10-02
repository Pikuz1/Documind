# DocuMind

Ask questions about German or English contracts (PDF) and get answers that cite the exact page they came from.

Work in progress — full documentation will follow.

## Quick start (any OS)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows, macOS) or Docker Engine (Linux).
2. Clone the repository:
   ```bash
   git clone https://github.com/Pikuz1/Documind.git && cd Documind
   ```
3. Copy `backend/.env.example` to `backend/.env` (required) and set `GOOGLE_API_KEY` to a free Gemini key from [Google AI Studio](https://aistudio.google.com/apikey).
   No key yet? Set `AI_PROVIDER=fake` instead to try the app with placeholder answers. Without either, the app stops at startup and tells you which one to set.
4. Start it:
   ```bash
   docker compose up --build
   ```
   The first build takes a few minutes. Then open <http://localhost:8000>.

Uploaded documents are indexed into a Docker volume (`app-data`), so they survive restarts. `docker compose down -v` removes them.
