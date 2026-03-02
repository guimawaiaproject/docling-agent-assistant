@echo off
cd /d "%~dp0"
echo Demarrage PWA sur https://localhost:5173
echo.
cd apps\pwa
pnpm exec vite
pause
