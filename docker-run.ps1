# Script para construir y ejecutar el contenedor Docker localmente

Write-Host "🐳 Construyendo imagen Docker para API..." -ForegroundColor Cyan
docker build -t hotel-reviews-api:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Imagen construida exitosamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Iniciando contenedor..." -ForegroundColor Cyan
    
    # Detener contenedor existente si existe
    docker stop hotel-reviews-api 2>$null
    docker rm hotel-reviews-api 2>$null
    
    # Iniciar nuevo contenedor
    docker run -d `
        --name hotel-reviews-api `
        -p 8000:8000 `
        -e PORT=8000 `
        hotel-reviews-api:latest
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Contenedor iniciado exitosamente" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Información del contenedor:" -ForegroundColor Yellow
        docker ps --filter name=hotel-reviews-api
        Write-Host ""
        Write-Host "🌐 API disponible en: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "📖 Documentación: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📝 Ver logs:" -ForegroundColor Yellow
        Write-Host "   docker logs -f hotel-reviews-api" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🛑 Detener contenedor:" -ForegroundColor Yellow
        Write-Host "   docker stop hotel-reviews-api" -ForegroundColor Gray
        Write-Host ""
        
        # Esperar unos segundos y verificar health
        Write-Host "⏳ Esperando que la API inicie..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
            Write-Host "✅ Health check exitoso!" -ForegroundColor Green
            $response.Content | ConvertFrom-Json | ConvertTo-Json
        } catch {
            Write-Host "⚠️  API aún iniciando o health check falló" -ForegroundColor Yellow
            Write-Host "   Verifica los logs: docker logs hotel-reviews-api" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Error al iniciar el contenedor" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Error al construir la imagen" -ForegroundColor Red
}
