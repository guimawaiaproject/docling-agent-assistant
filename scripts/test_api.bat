@echo off
REM Test E2E de l'API Docling Agent
REM L'API doit etre demarree (python api.py) avant d'executer ce script.
echo.
python "%~dp0test_api_e2e.py" %*
exit /b %ERRORLEVEL%
