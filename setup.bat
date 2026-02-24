@echo off
setlocal enabledelayedexpansion
echo ==========================================
echo   DOCLING AGENT v2 - INSTALLATION
echo ==========================================
echo.

:: --- ETAPE 0 : RECHERCHE DE PYTHON ---
set PY_CMD=none
python --version >nul 2>&1
if %errorlevel% equ 0 (set PY_CMD=python)
if "!PY_CMD!"=="none" (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (set PY_CMD=py)
)
if "!PY_CMD!"=="none" (
    echo [ERREUR] Python n'est pas installe.
    echo Telechargez Python 3.11+ sur https://www.python.org/downloads/
    pause
    exit /b
)

echo [INFO] Python detecte : !PY_CMD!
echo.

:: --- ETAPE 1 : VENV ---
if not exist venv (
    echo [1/4] Creation de l'environnement virtuel...
    !PY_CMD! -m venv venv
    if %errorlevel% neq 0 (
        echo [ERREUR] Echec de creation du venv.
        pause
        exit /b
    )
)

:: --- ETAPE 2 : MISE A JOUR PIP ---
echo [2/4] Mise a jour de pip...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet

:: --- ETAPE 3 : INSTALLATION ---
echo [3/4] Installation des bibliotheques...
venv\Scripts\pip.exe install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] L'installation a echoue.
    pause
    exit /b
)

:: --- ETAPE 4 : LANCEMENT ---
echo.
echo [4/4] Lancement de l'application...
echo.
echo ==========================================
echo   Ouvrez : http://localhost:8501
echo ==========================================
echo.
venv\Scripts\streamlit.exe run app.py
pause
