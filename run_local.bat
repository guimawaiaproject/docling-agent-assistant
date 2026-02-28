@echo off
setlocal enabledelayedexpansion
TITLE Docling Agent v3 - Launcher
COLOR 0B

echo ============================================================
echo      DOCLING AGENT v3 - LANCEMENT LOCAL (BTP EDITION)
echo ============================================================
echo.

:: 0. PRE-LAUNCH CHECK (verification 100%% avant lancement)
echo [0/3] Pre-launch check (lint, build, tests)...
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\pre_launch_check.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Pre-launch check echoue. Corriger les erreurs avant de lancer.
    pause
    exit /b 1
)
echo [OK] Pre-launch check valide.
echo.

:: Nettoyage cible sur les ports 8000 et 5173 uniquement (evite de tuer d'autres projets)
echo [1/3] Nettoyage des processus sur ports 8000 et 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173 "') do taskkill /F /PID %%a >nul 2>&1

:: 1. Verification du VENV
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Environnement virtuel Python manquant.
    echo Veuillez executer: python -m venv venv
    pause
    exit /b
)

:: 2. Lancement du Backend
echo [2/3] Demarrage du Backend FastAPI (Port 8000)...
start "Backend - FastAPI" cmd /k ".\venv\Scripts\python.exe api.py"

:: 3. Lancement du Frontend
echo [3/3] Demarrage du Frontend PWA (Port 5173)...
if exist "docling-pwa\package.json" (
    :: On utilise npx vite pour etre sur que la commande est trouvee
    start "Frontend - Vite PWA" cmd /k "cd docling-pwa && npx vite"
) else (
    echo [WARNING] Dossier docling-pwa introuvable.
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
