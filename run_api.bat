@echo off
cd /d "%~dp0"
echo Demarrage API sur http://localhost:8000
echo.
cd apps\api
uv run uvicorn main:app --host 0.0.0.0 --port 8000
pause
