$ErrorActionPreference = "Stop"
Push-Location client
npm run dev -- --host 0.0.0.0 --port 5173
Pop-Location
