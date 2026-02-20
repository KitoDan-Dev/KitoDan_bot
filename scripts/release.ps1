$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "[1/6] Installing build dependencies"
& "server/.venv/Scripts/python.exe" -m pip install -r server/requirements-build.txt

Write-Host "[2/6] Building client"
Push-Location client
npm install
npm run build
Pop-Location

Write-Host "[3/6] Building server exe"
& "server/.venv/Scripts/python.exe" -m PyInstaller --noconfirm installer/kitodan-server.spec

Write-Host "[4/6] Building tray exe"
& "server/.venv/Scripts/python.exe" -m PyInstaller --noconfirm installer/kitodan-tray.spec

if (-not (Test-Path "release")) { New-Item -ItemType Directory -Path "release" | Out-Null }

$isccPaths = @(
  "$Env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
  "$Env:ProgramFiles\Inno Setup 6\ISCC.exe"
)
$iscc = $isccPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($null -ne $iscc) {
  Write-Host "[5/6] Building installer"
  & $iscc "installer/KitoDan.iss"
} else {
  Write-Warning "ISCC.exe not found. Install Inno Setup 6 to generate KitoDanSetup.exe."
}

Write-Host "[6/6] Generating release notes and checksums"
$version = "0.3.0"
$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$notes = @"
KitoDan Release
Version: $version
Date: $date
Artifacts:
- dist/kitodan-server.exe
- dist/kitodan-tray.exe
- release/KitoDanSetup.exe (if ISCC installed)
"@
$notes | Out-File -Encoding utf8 "release/notes.txt"

$targets = @("dist/kitodan-server.exe", "dist/kitodan-tray.exe", "release/KitoDanSetup.exe") | Where-Object { Test-Path $_ }
$checksums = foreach ($t in $targets) { Get-FileHash $t -Algorithm SHA256 }
$checksums | ForEach-Object { "$($_.Hash)  $($_.Path)" } | Out-File -Encoding utf8 "release/checksums.txt"

Write-Host "Release process complete."
