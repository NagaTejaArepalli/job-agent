# Setup Windows Task Scheduler to run Job Discovery everyday at 08:30 AM
# Runs 100% locally on your PC without publishing to any website or cloud!

$taskName = "AI_Job_Agent_Daily_Discovery"
$pythonPath = (Get-Command python).Source
$scriptPath = (Resolve-Path "backend\run_daily.py").Path
$workingDir = (Get-Location).Path

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Register Windows Daily Task (100% Local PC Execution)   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Python:     $pythonPath" -ForegroundColor Gray
Write-Host "Script:     $scriptPath" -ForegroundColor Gray
Write-Host "WorkingDir: $workingDir" -ForegroundColor Gray
Write-Host "Time:       08:30 AM Daily" -ForegroundColor Yellow
Write-Host ""

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`"" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At 8:30AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily AI Job Discovery & Application Agent for Naga Teja Arepalli" -Force | Out-Null
    Write-Host "SUCCESS: Windows Task '$taskName' registered successfully!" -ForegroundColor Green
    Write-Host "Windows will now run your job discovery automatically every day at 08:30 AM." -ForegroundColor Green
    Write-Host "No cloud hosting, domain, or publishing required." -ForegroundColor Cyan
} catch {
    # Fallback to schtasks command if Register-ScheduledTask requires elevation
    Write-Host "Registering via schtasks..." -ForegroundColor Yellow
    & schtasks /create /tn $taskName /tr "`"$pythonPath`" `"$scriptPath`"" /sc daily /st 08:30 /f
}
