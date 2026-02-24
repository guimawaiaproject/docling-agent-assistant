#!/bin/bash
set -e

echo "=========================================="
echo "   DOCLING AGENT v2 - INSTALLATION"
echo "=========================================="
echo

if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python3 n'est pas installe."
    echo "Installez Python 3.11+ : https://www.python.org/downloads/"
    exit 1
fi

echo "[INFO] $(python3 --version) detecte"
echo

if [ ! -d "venv" ]; then
    echo "[1/4] Creation de l'environnement virtuel..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "[2/4] Mise a jour de pip..."
pip install --upgrade pip --quiet

echo "[3/4] Installation des bibliotheques..."
pip install -r requirements.txt --quiet

echo
echo "[4/4] Lancement de l'application..."
echo
echo "=========================================="
echo "   Ouvrez : http://localhost:8501"
echo "=========================================="
echo
streamlit run app.py
