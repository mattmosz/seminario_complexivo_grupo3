@echo off
cd /d "C:\Users\Zona Informatica\Desktop\seminario_complexivo_grupo3"

REM Levanta la API
start cmd /k "uvicorn api_app:app --host 0.0.0.0 --port 8000"

REM Espera 3 seg y levanta ngrok
timeout /t 3 >nul
start cmd /k "ngrok http 8000"

REM Abre el inspector (ver requests y errores)
start http://127.0.0.1:4040

REM Tip: para ver la URL pública en consola:
REM powershell -Command "Invoke-RestMethod http://127.0.0.1:4040/api/tunnels | % tunnels | % public_url"
