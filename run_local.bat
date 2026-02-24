@echo off
setlocal
cd /d %~dp0

echo "Lancement de Docling Agent (Local Mode - Sans Docker)"
echo.

:: Démarrer l'API FastAPI en arrière-plan
echo [1/2] Lancement de l'API (FastAPI)...
start "Docling Agent - API" cmd /c ".\venv\Scripts\python.exe -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload"

:: Attendre 3 secondes que l'API soit prête
ping 127.0.0.1 -n 4 > nul

:: Démarrer Streamlit en premier plan
echo [2/2] Lancement du Web Client (Streamlit)...
.\venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
