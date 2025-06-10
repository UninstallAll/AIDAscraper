@echo off
echo Starting ArtScraper - Web Scraping Tool...

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Set environment variables
set PYTHONPATH=%~dp0
set DATA_DIR=%~dp0data

:: Install required dependencies if needed
python -c "import spacy" 2>nul || (
  echo Installing additional dependencies...
  pip install -r requirements.txt
  
  echo Downloading spaCy language model...
  python -m spacy download en_core_web_sm
)

:: Create data directories
if not exist "%DATA_DIR%" (
  echo Creating data directories...
  mkdir "%DATA_DIR%"
  mkdir "%DATA_DIR%\search_results"
  mkdir "%DATA_DIR%\scraped_data"
)

:: Start API service (in a new window)
start "ArtScraper API" cmd /c "cd %~dp0 && call venv\Scripts\activate.bat && cd src\api && python app.py"

:: Wait 2 seconds to ensure API service starts first
timeout /t 2 > nul

:: Start frontend service (in a new window)
start "ArtScraper Frontend" cmd /c "cd %~dp0\frontend && npm run dev"

:: Wait 3 seconds for frontend to initialize
timeout /t 3 > nul

:: Automatically open browser to the frontend URL
start http://localhost:3000

echo.
echo System started!
echo API service running at: http://localhost:8000
echo Frontend service running at: http://localhost:3000
echo Browser window should open automatically.
echo.
echo Press any key to exit this window (this will not close the running services)
pause > nul 