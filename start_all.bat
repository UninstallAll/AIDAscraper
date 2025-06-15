@echo off
echo AIDA Scraper - One-Click Startup
echo ===============================
echo.

REM Set environment variables
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Please install Python and make sure it's in your PATH
    exit /b 1
)

echo 1. Initializing database...
cd scraper
python start.py --init-db
if %errorlevel% neq 0 (
    echo Error: Failed to initialize database
    exit /b 1
)
echo Database initialized successfully
echo.

echo 2. Starting API server in background...
start "AIDA Scraper API" cmd /c "python start.py --start-api --no-reload"
echo API server started at http://localhost:8000
echo.

echo 3. Starting Celery worker in background...
start "AIDA Scraper Worker" cmd /c "python start_worker.py"
echo Celery worker started
echo.

echo 4. Running SaatchiArt spider test...
python run_saatchi_spider.py
echo.

echo All components started successfully!
echo.
echo API Documentation: http://localhost:8000/docs
echo API Endpoints: http://localhost:8000/api/v1/
echo. 