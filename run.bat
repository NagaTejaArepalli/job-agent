@echo off
echo ==========================================================
echo    AI Job Search ^& Application Agent (Everyday System)
echo ==========================================================

echo [1/2] Starting Backend Server on http://localhost:8000...
start "Backend API Server" python -m uvicorn backend.main:app --port 8000 --reload

echo [2/2] Starting Frontend Vite Server on http://localhost:5173...
cd frontend
start "Frontend Dashboard" npm run dev
cd ..

echo.
echo Application started!
echo Dashboard URL: http://localhost:5173
echo Backend API:   http://localhost:8000/docs
echo.
pause
