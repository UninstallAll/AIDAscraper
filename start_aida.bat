@echo off
setlocal enabledelayedexpansion

:: Set title for main console window
title AIDA Art Data Scraper Control Panel

:: Color settings
color 0A

:MENU
cls
echo ===================================================
echo        AIDA Art Data Scraper - Control Panel
echo ===================================================
echo.
echo  [1] Start Complete System (API + Frontend + Scraper)
echo  [2] Start API and Frontend Only
echo  [3] Start Individual Component
echo  [4] Manage Websites and Scrapers
echo  [5] Stop All Services
echo  [6] Environment Setup and Check
echo  [7] Open Website Manager UI
echo  [X] Exit
echo.
echo ===================================================
echo.
set /p choice="Enter your choice (1-7 or X): "

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto START_CORE
if "%choice%"=="3" goto START_INDIVIDUAL
if "%choice%"=="4" goto MANAGE_WEBSITES
if "%choice%"=="5" goto STOP_SERVICES
if "%choice%"=="6" goto ENV_CHECK
if "%choice%"=="7" goto OPEN_WEBSITE_MANAGER
if /i "%choice%"=="X" exit
if /i "%choice%"=="x" exit

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MENU

:ENV_CHECK
cls
echo ===================================================
echo          Environment Setup and Check
echo ===================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    goto ENV_CHECK_FAILED
)

:: Check for virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo Would you like to create a new virtual environment? (Y/N)
    set /p create_venv=
    if /i "!create_venv!"=="Y" (
        python -m venv venv
        call venv\Scripts\activate.bat
        pip install -r requirements.txt
    ) else (
        goto ENV_CHECK_FAILED
    )
) else (
    call venv\Scripts\activate.bat
)

:: Check Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set pyver=%%a
echo Python Version: %pyver%
echo Virtual Environment: %VIRTUAL_ENV%

:: Check for npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm not found. Please install Node.js and npm.
    goto ENV_CHECK_FAILED
)

:: Check frontend dependencies
if not exist "frontend\node_modules" (
    echo Frontend dependencies not found. Installing...
    cd frontend
    npm install
    cd ..
)

echo.
echo Environment check completed successfully!
echo All required components are installed.
echo.
pause
goto MENU

:ENV_CHECK_FAILED
echo.
echo Environment check failed. Please resolve the issues and try again.
echo.
pause
goto MENU

:START_ALL
cls
echo ===================================================
echo     Starting Complete AIDA Scraper System
echo ===================================================
echo.

call :START_API
if %errorlevel% neq 0 goto START_FAILED

call :START_FRONTEND
if %errorlevel% neq 0 goto START_FAILED

call :START_SCRAPER
if %errorlevel% neq 0 goto START_FAILED

echo.
echo System Started Successfully!
echo ===================================================
echo API service running at: http://localhost:8000
echo Frontend service running at: http://localhost:3000
echo Scraper engine is running in background
echo ===================================================
echo.
pause
goto MENU

:START_CORE
cls
echo ===================================================
echo     Starting AIDA Core Services (API + Frontend)
echo ===================================================
echo.

call :START_API
if %errorlevel% neq 0 goto START_FAILED

call :START_FRONTEND
if %errorlevel% neq 0 goto START_FAILED

echo.
echo Core Services Started Successfully!
echo ===================================================
echo API service running at: http://localhost:8000
echo Frontend service running at: http://localhost:3000
echo ===================================================
echo.
pause
goto MENU

:START_INDIVIDUAL
cls
echo ===================================================
echo          Start Individual Component
echo ===================================================
echo.
echo  [A] Start API Service
echo  [F] Start Frontend
echo  [S] Start Scraper Engine
echo  [B] Back to Main Menu
echo.
echo ===================================================
echo.
set /p comp="Enter component to start (A/F/S/B): "

if /i "%comp%"=="A" (
    call :START_API
    pause
    goto MENU
)

if /i "%comp%"=="F" (
    call :START_FRONTEND
    pause
    goto MENU
)

if /i "%comp%"=="S" (
    call :START_SCRAPER
    pause
    goto MENU
)

if /i "%comp%"=="B" goto MENU

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto START_INDIVIDUAL

:MANAGE_WEBSITES
cls
echo ===================================================
echo              Website Manager
echo ===================================================
echo.
echo  [1] List All Websites
echo  [2] Add New Website
echo  [3] Create Website Scraper
echo  [4] Run Specific Website Scraper
echo  [5] Back to Main Menu
echo.
echo ===================================================
echo.
set /p web_choice="Enter choice (1-5): "

if "%web_choice%"=="1" (
    call :WEBSITE_LIST
    pause
    goto MANAGE_WEBSITES
)

if "%web_choice%"=="2" (
    call :WEBSITE_ADD
    pause
    goto MANAGE_WEBSITES
)

if "%web_choice%"=="3" (
    call :WEBSITE_CREATE_SCRAPER
    pause
    goto MANAGE_WEBSITES
)

if "%web_choice%"=="4" (
    call :WEBSITE_RUN_SCRAPER
    pause
    goto MANAGE_WEBSITES
)

if "%web_choice%"=="5" goto MENU

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MANAGE_WEBSITES

:WEBSITE_LIST
echo.
echo Listing all registered websites...
call venv\Scripts\activate.bat
python -m src.main sites list --verbose
exit /b 0

:WEBSITE_ADD
echo.
echo Adding new website...
echo.
set /p site_id="Enter website ID (e.g. met_museum): "
set /p site_name="Enter website name: "
set /p site_url="Enter website URL: "
set /p site_desc="Enter description (optional): "

call venv\Scripts\activate.bat
if "%site_desc%"=="" (
    python -m src.main sites add --id "%site_id%" --name "%site_name%" --url "%site_url%"
) else (
    python -m src.main sites add --id "%site_id%" --name "%site_name%" --url "%site_url%" --description "%site_desc%"
)
exit /b 0

:WEBSITE_CREATE_SCRAPER
echo.
echo Creating website-specific scraper...
echo.
set /p site_id="Enter website ID: "
set /p scraper_name="Enter scraper class name: "

call venv\Scripts\activate.bat
python -m src.main sites create-scraper --id "%site_id%" --name "%scraper_name%"
exit /b 0

:WEBSITE_RUN_SCRAPER
echo.
echo Running website scraper...
echo.
set /p site_id="Enter website ID: "
set /p content_type="Enter content type (artworks/artists/exhibitions) [artworks]: "
set /p pages="Enter max pages [1]: "
set /p limit="Enter items per page [20]: "

if "%content_type%"=="" set content_type=artworks
if "%pages%"=="" set pages=1
if "%limit%"=="" set limit=20

call venv\Scripts\activate.bat
python -m src.main sites run --id "%site_id%" --content "%content_type%" --pages %pages% --limit %limit%
exit /b 0

:STOP_SERVICES
cls
echo ===================================================
echo            Stopping All Services
echo ===================================================
echo.
echo Stopping services...

:: Kill processes by window title (created with "start" command)
taskkill /fi "WindowTitle eq AIDA API*" /T /F >nul 2>&1
taskkill /fi "WindowTitle eq AIDA Frontend*" /T /F >nul 2>&1
taskkill /fi "WindowTitle eq AIDA Scraper Engine*" /T /F >nul 2>&1

echo All services have been stopped.
echo.
pause
goto MENU

:START_FAILED
echo.
echo [ERROR] Failed to start one or more components.
echo Please check the error messages above and try again.
echo.
pause
goto MENU

:: Helper functions for starting individual components
:START_API
echo Starting API Service...
call venv\Scripts\activate.bat
start "AIDA API" cmd /c "cd %~dp0 && call venv\Scripts\activate.bat && cd src\api && python app.py"
timeout /t 2 >nul
exit /b 0

:START_FRONTEND
echo Starting Frontend Service...
start "AIDA Frontend" cmd /c "cd %~dp0\frontend && npm run dev"
timeout /t 3 >nul

:: Automatically open browser to the frontend URL
start http://localhost:3000
exit /b 0

:START_SCRAPER
echo Starting Scraper Engine...
call venv\Scripts\activate.bat
echo.
echo Enter scraper parameters (leave empty for defaults):
set site=
set limit=100
set debug=

set /p site="Target site (optional): "
set /p limit="Item limit (default: 100): "
set /p debug_mode="Enable debug mode? (Y/N, default: N): "

set params=
if not "%site%"=="" set params=!params! --site=%site%
if not "%limit%"=="" set params=!params! --limit=%limit%
if /i "%debug_mode%"=="Y" set params=!params! --debug

start "AIDA Scraper Engine" cmd /c "cd %~dp0 && call venv\Scripts\activate.bat && python -m src.main scrape !params!"
exit /b 0

:OPEN_WEBSITE_MANAGER
echo.
echo Opening Website Manager UI...

:: Check if services are running
tasklist /fi "WindowTitle eq AIDA API*" >nul 2>&1
if %errorlevel% neq 0 (
    echo API service is not running. Starting API first...
    call :START_API
    timeout /t 3 >nul
)

tasklist /fi "WindowTitle eq AIDA Frontend*" >nul 2>&1
if %errorlevel% neq 0 (
    echo Frontend is not running. Starting Frontend first...
    call :START_FRONTEND
    timeout /t 3 >nul
)

:: Open the website manager page in browser
start http://localhost:3000/#/website-manager
echo Website Manager opened in your browser.
echo.
pause
goto MENU 