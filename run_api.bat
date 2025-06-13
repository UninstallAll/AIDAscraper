@echo off
echo Starting AIDA API Server...
call venv\Scripts\activate.bat
cd src\api
python app.py 