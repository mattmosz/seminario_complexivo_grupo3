# CHECKLIST: Deployment Dashboard en Streamlit Cloud

## Archivos Preparados

- `dashboard/requirements.txt` - Solo 7 librerías (UI únicamente)
- `dashboard/.streamlit/config.toml` - Configuración optimizada
- `dashboard/.streamlit/secrets.toml.example` - Template de secrets
- `dashboard/.streamlitignore` - Archivos a ignorar
- `dashboard/DEPLOYMENT.md` - Guía completa
- `.gitignore` actualizado - Protege secrets locales

## Pasos para Desplegar

### 1. Subir cambios a GitHub
```bash
git add .
git commit -m "Prepare dashboard for Streamlit Cloud deployment"
git push origin main
```

### 2. Desplegar API en Render (si aún no está)
- Ve a https://render.com
- Conecta tu repo
- Render detectará el `Dockerfile` y `render.yaml`
- Espera ~5-10 minutos
- Obtén la URL: `https://tu-api.onrender.com`

### 3. Configurar Streamlit Cloud
1. Ve a https://share.streamlit.io
2. New app → Selecciona tu repo
3. **Main file path**: `dashboard/app.py`
4. **Python version**: 3.11
5. En **Advanced settings** → **Secrets**, agrega:
   ```toml
   API_URL = "https://tu-api.onrender.com"
   API_TIMEOUT = 30
   ```
6. Click **Deploy**

### 4. Verificar
- Dashboard: `https://tu-app.streamlit.app`
- Debe aparecer "API CONECTADA" en la esquina superior
- Prueba cada tab del dashboard

## Dependencias Optimizadas

### Dashboard (solo visualización - 7 librerías)
```
streamlit==1.38.0      # Framework
plotly==5.24.1         # Gráficos
pandas==2.2.2          # Datos
numpy==1.26.4          # Cálculos
requests==2.32.3       # API client
wordcloud==1.9.3       # Nubes
Pillow==10.4.0         # Imágenes
```

### API (procesamiento backend - 9 librerías)
```
fastapi==0.110.0
uvicorn==0.27.1
pydantic==2.6.1
pandas==2.2.0
numpy==1.26.3
nltk==3.8.1
scikit-learn==1.4.0
vaderSentiment==3.3.2
python-multipart==0.0.9
```

## Arquitectura Final

```
GitHub Repo
    ├── dashboard/ ──────────────┐
    │   ├── app.py               │
    │   ├── requirements.txt     │
    │   └── .streamlit/          │
    │                            │
    ├── api_app.py ──────────────┼────┐
    ├── requirements-api.txt     │    │
    ├── Dockerfile              │    │
    └── render.yaml             │    │
                                 │    │
                                 ▼    ▼
                    Streamlit Cloud  Render
                    (Frontend UI)    (Backend API)
                         │              │
                         └──── HTTPS ───┘
```

## Tiempos Estimados

- **Streamlit Cloud**: 3-5 minutos
- **Render (Docker)**: 5-10 minutos
- **Total**: ~10-15 minutos

## Verificación Post-Deployment

### API Health Check
```bash
curl https://tu-api.onrender.com/health
```
Debe retornar:
```json
{
  "status": "healthy",
  "dataset_loaded": true,
  "total_reviews": 
}
```

### Dashboard Connection
1. Abre `https://tu-app.streamlit.app`
2. Busca en la esquina superior: **API CONECTADA** (verde)
3. Si ves **API NO DISPONIBLE** (rojo):
   - Verifica URL en secrets
   - Confirma que API esté corriendo
   - Revisa CORS en la API

## Troubleshooting Rápido

### "Your app is on the oven" > 10 minutos
- **Causa**: Error en instalación de dependencias
- **Solución**: Revisar logs en Streamlit Cloud → "Manage app" → "Logs"

### "API NO DISPONIBLE"
- **Causa**: URL incorrecta o API caída
- **Solución**: 
  1. Verificar `API_URL` en secrets
  2. Probar `https://tu-api.onrender.com/health`
  3. Reiniciar API en Render si está "sleeping"

### Dashboard carga pero sin datos
- **Causa**: API responde pero con errores
- **Solución**: Ver logs de la API en Render

## URLs Finales

Una vez desplegado, tendrás:

- **Dashboard**: https://[tu-nombre]-hotel-reviews.streamlit.app
- **API**: https://hotel-reviews-api.onrender.com
- **API Docs**: https://hotel-reviews-api.onrender.com/docs
- **GitHub**: https://github.com/mattmosz/seminario_complexivo_grupo3

## ¡Listo para Producción!

Tu aplicación ahora tiene:
- Frontend ligero y rápido en Streamlit Cloud
- Backend robusto en contenedor Docker
- Separación total de concerns
- Escalable independientemente
- Documentación completa
- Secrets protegidos
- Ready para presentar

---

**Próximo paso**: `git push origin main` y desplegar 
