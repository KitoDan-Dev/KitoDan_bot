$ErrorActionPreference = "Stop"

Write-Host "Server: http://localhost:4891"
Write-Host "Client (dev): http://localhost:5173"

Start-Process powershell -ArgumentList "-NoExit", "-File", "scripts/run_server.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "scripts/run_client.ps1"
