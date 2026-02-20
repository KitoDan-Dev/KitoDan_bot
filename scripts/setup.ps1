$ErrorActionPreference = "Stop"

function Require-Cmd($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "$name is required but not installed."
  }
}

Require-Cmd "python"
Require-Cmd "node"
Require-Cmd "npm"

if (-not (Test-Path "server/.venv")) {
  python -m venv server/.venv
}

& "server/.venv/Scripts/python.exe" -m pip install -r server/requirements.txt

Push-Location client
npm install
Pop-Location

if (-not (Test-Path "server/.env")) { Copy-Item "server/.env.example" "server/.env" }
if (-not (Test-Path "client/.env")) { Copy-Item "client/.env.example" "client/.env" }

Write-Host "Setup completed."
