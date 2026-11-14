@echo off
echo ==========================================================
echo   Register Windows Daily Task (100% Local PC Execution)
echo ==========================================================

for /f "delims=" %%i in ('where python') do set PYTHON_EXE=%%i & goto :found
:found

echo Python Path: %PYTHON_EXE%
echo Working Dir: %~dp0

schtasks /create /tn "AI_Job_Agent_Daily_Discovery" /tr "\"%PYTHON_EXE%\" \"%~dp0backend\run_daily.py\"" /sc daily /st 08:30 /f

echo.
echo Windows will now automatically run job discovery every day at 08:30 AM!
echo No cloud hosting or website publishing needed.
echo.
pause
