# KitoDan Local MVP (FastAPI + React + Ollama)

KitoDan runs as a local app with:
- **Single local server process** serving API and React static files
- **API prefix**: `/api/*`
- **Default URL**: `http://localhost:4891`
- **Persistent data** in `%APPDATA%\KitoDan`

## Runtime layout (installed)
- Config: `%APPDATA%\KitoDan\server.env`
- DB: `%APPDATA%\KitoDan\data\kitodan.db`
- Logs: `%APPDATA%\KitoDan\logs\server.log`

## Dev mode (Windows PowerShell)
1. Install prerequisites: Python 3.10+, Node 18+, npm, Ollama.
2. Start Ollama + model:
   ```powershell
   ollama serve
   ollama pull llama3.1:8b
   ```
3. Setup project:
   ```powershell
   ./scripts/setup.ps1
   ```
4. Run dev server/client:
   ```powershell
   ./scripts/run.ps1
   ```

## API endpoints
- `GET /api/health`
- `POST /api/chat`
- `GET /api/history?sessions=1`
- `GET /api/history/{session_id}`
- `POST /api/reset`
- `POST /api/session/title`

## Build release (Windows)
> End users do **not** need Python/Node. They only run the installer.

### Build dependencies
- Python venv in `server/.venv`
- Node/npm
- Inno Setup 6 (`ISCC.exe`) for installer generation

Install Inno Setup: https://jrsoftware.org/isdl.php
Expected path (auto-detected by script):
- `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

### One-command release
```powershell
./scripts/release.ps1
```

This script:
1. Builds React (`client/dist`)
2. Builds `dist/kitodan-server.exe` (PyInstaller)
3. Builds `dist/kitodan-tray.exe` (PyInstaller)
4. Builds `release/KitoDanSetup.exe` (if ISCC installed)
5. Generates `release/checksums.txt` and `release/notes.txt`

## Installer details
- Inno Setup script: `installer/KitoDan.iss`
- Installs to: `{autopf}\KitoDan`
- Creates desktop/start menu shortcuts
- Options:
  - Run KitoDan after install (default checked)
  - Start with Windows (HKCU Run)
- Ollama detection is non-blocking (install continues with guidance)

## Dev vs Installed
- **Dev**: Vite + FastAPI separate, Vite proxies `/api`.
- **Installed**: one process (`kitodan-server.exe`) serves API and static UI.

## Troubleshooting
- **Firewall prompt**: allow app on private network.
- **Port occupied**: change `PORT` in `%APPDATA%\KitoDan\server.env`.
- **Ollama offline**: run `ollama serve`.
- **Model missing**: run `ollama pull llama3.1:8b`.
- **Client not loading**: ensure `client/dist` exists in build or reinstall.
