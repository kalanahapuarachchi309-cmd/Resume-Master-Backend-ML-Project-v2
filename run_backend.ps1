# PowerShell script to run the Resume Master FastAPI backend
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting Resume Master FastAPI & ML Backend Server    " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "URL: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

& "$scriptDir\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
