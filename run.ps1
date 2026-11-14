# Launch AI Job Search & Application Agent (Backend & Frontend)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AI Job Search & Application Agent (Everyday System)   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Backend FastAPI Server
Write-Host "[1/2] Starting Backend Server on http://localhost:8000..." -ForegroundColor Yellow
$backendProcess = Start-Process python -ArgumentList "-m uvicorn backend.main:app --port 8000 --reload" -PassThru

# 2. Start Frontend Dev Server
Write-Host "[2/2] Starting Frontend Vite Server on http://localhost:5173..." -ForegroundColor Yellow
Set-Location frontend
$frontendProcess = Start-Process npm -ArgumentList "run dev" -PassThru
Set-Location ..

Write-Host ""
Write-Host "Application is running!" -ForegroundColor Green
Write-Host "Dashboard URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend API:   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C or close the terminal windows to stop." -ForegroundColor Gray
