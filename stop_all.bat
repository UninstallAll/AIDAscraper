@echo off
echo AIDA Scraper - Stopping All Services
echo ==================================
echo.

echo Stopping all Python processes...
taskkill /F /FI "WINDOWTITLE eq AIDA Scraper API*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq AIDA Scraper Worker*" /T >nul 2>&1

echo Stopping any remaining Python processes...
taskkill /F /IM python.exe /T >nul 2>&1

echo Stopping Celery workers...
taskkill /F /IM celery.exe /T >nul 2>&1

echo All services stopped successfully!
echo.
echo Press any key to exit
pause 