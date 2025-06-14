@echo off
echo AIDA Scraper Auto Execution Script
echo ================================

REM Check if PowerShell is available
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell not found
    exit /b 1
)

echo Starting automated command execution...
powershell -ExecutionPolicy Bypass -File auto_approve.ps1 -CommandsFile commands.txt -DefaultTimeout 60 -LogFile auto_run.log

echo Execution completed, see auto_run.log for details
pause 