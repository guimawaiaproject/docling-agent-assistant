@echo off
setlocal enabledelayedexpansion
TITLE Docling Agent v3 - Launcher
COLOR 0B

:: Se placer dans le dossier du script (racine projet)
cd /d "%~dp0"
set "ROOT=%~dp0"

echo ============================================================
echo      DOCLING AGENT v3 - LANCEMENT LOCAL (BTP EDITION)
echo ============================================================
echo.
echo [TIP] Validation complete: powershell -File scripts\validate_all.ps1
echo.

:: Nettoyage cible sur les ports 8000 et 5173 uniquement (evite de tuer d'autres projets)
echo [1/3] Nettoyage des processus sur ports 8000 et 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173 "') do taskkill /F /PID %%a >nul 2>&1

:: 1. Verification apps/api (uv)
if not exist "apps\api\pyproject.toml" (
    echo [ERROR] apps/api introuvable.
    pause
    exit /b 1
)
where uv >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uv manquant. Installer: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

:: 2. Lancement du Backend
echo [2/3] Demarrage du Backend FastAPI (Port 8000)...
start "Backend - FastAPI" cmd /k "cd /d %ROOT%apps\api && uv run uvicorn main:app --host 0.0.0.0 --port 8000"

:: 3. Lancement du Frontend
echo [3/3] Demarrage du Frontend PWA (Port 5173)...
if exist "apps\pwa\package.json" (
    start "Frontend - Vite PWA" cmd /k "cd /d %ROOT%apps\pwa && pnpm exec vite"
) else (
    echo [WARNING] Dossier apps/pwa introuvable.
)

echo.
echo ------------------------------------------------------------
echo [SUCCESS] Les deux services sont en cours de demarrage.
echo.
echo URL API  : http://localhost:8000
echo URL PWA  : http://localhost:5173
echo ------------------------------------------------------------
echo.
echo Appuyez sur une touche pour quitter ce lanceur.
pause > nul
