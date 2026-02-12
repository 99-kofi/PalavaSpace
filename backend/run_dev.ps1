$BACKEND_DIR = Get-Location
# NOTE: PowerShell may show server logs in red text (NativeCommandError). This is normal and means the server is running.
$VENV_PYTHON = "$BACKEND_DIR\venv\Scripts\python.exe"

$PRISMA_EXE = "$BACKEND_DIR\venv\Scripts\prisma.exe"

Write-Host "--- PALAVASPACE BOOT ---" -ForegroundColor Cyan

# Kill any existing python processes for this project
Write-Host "Cleaning up old processes..." -ForegroundColor Yellow
$oldProcs = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*PALAVASPACE*" }
if ($oldProcs) { 
    $oldProcs | Stop-Process -Force 
}

# Clear Port 5050
$portProc = Get-NetTCPConnection -LocalPort 5050 -ErrorAction SilentlyContinue
if ($portProc) {
    Write-Host "Clearing Port 5050..." -ForegroundColor Yellow
    Stop-Process -Id $portProc.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Write-Host "Syncing DB..." -ForegroundColor Yellow
# & $PRISMA_EXE generate

Write-Host "Launching Arena on http://localhost:5050" -ForegroundColor Green
& $VENV_PYTHON app.py
