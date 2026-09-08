@echo off
echo ========================================================
echo   Starting Resume Master FastAPI & ML Backend Server
echo ========================================================
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
pause
