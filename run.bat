@echo off
echo ==========================================================
echo    AI Job Search ^& Application Agent (Naga Teja Arepalli)
echo ==========================================================

echo [1/2] Starting Server on http://127.0.0.1:8000...
start "AI Job Agent Server" python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

timeout /t 2 /nobreak >nul

echo [2/2] Opening Dashboard in your browser...
start http://127.0.0.1:8000

echo.
echo Application is running!
echo Dashboard: http://127.0.0.1:8000
echo.
pause
