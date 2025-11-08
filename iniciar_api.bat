@echo off
echo === Iniciando API Docker ===
docker start hotel_api
timeout /t 3 >nul
echo === Abriendo tunel publico con ngrok ===
ngrok http 8000
pause
echo === API Iniciada ===