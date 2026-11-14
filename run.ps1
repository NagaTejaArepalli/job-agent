# Launch AI Job Search & Application Agent (Backend & Frontend)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AI Job Search & Application Agent (Naga Teja Arepalli) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Backend Server
Write-Host "[1/2] Starting Backend Server on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendProcess = Start-Process python -ArgumentList "-m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -PassThru

# Give server 2 seconds to initialize
Start-Sleep -Seconds 2

# 2. Automatically open your browser to the application
Write-Host "[2/2] Opening Dashboard in your browser..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

Write-Host ""
Write-Host "Application is live!" -ForegroundColor Green
Write-Host "Dashboard URL: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Swagger:   http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C or close this window to stop the server." -ForegroundColor Gray
