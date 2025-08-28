# Guía de Instalación y Configuración

## 🚀 Inicio Rápido

### 1. Preparación del Entorno

```bash
# Clonar el repositorio
git clone <tu-repo-url>
cd proyecto_logista_v1

# Copiar configuración
cp .env.example .env
```

### 2. Elegir Proveedor de IA

#### Opción A: Ollama (Recomendado para desarrollo)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.2

# Configurar .env
echo "LLM_PROVIDER=ollama" >> .env
```

#### Opción B: OpenAI (Recomendado para producción)
```bash
# Obtener API Key de https://platform.openai.com/api-keys
# Configurar .env
echo "LLM_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=tu-api-key-aqui" >> .env
```

### 3. Ejecutar la Aplicación

```bash
# Construir y ejecutar
docker-compose up -d --build

# Verificar estado
curl http://localhost:8000/llm-status
```

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valores | Default |
|----------|-------------|---------|---------|
| `LLM_PROVIDER` | Proveedor de IA | `openai`, `ollama` | `openai` |
| `OPENAI_API_KEY` | Clave API de OpenAI | `sk-...` | - |
| `OLLAMA_MODEL` | Modelo de Ollama | `llama3.2`, `llama2`, etc. | `llama3.2` |
| `OLLAMA_BASE_URL` | URL de Ollama | URL completa | `http://host.docker.internal:11434` |

### Modelos Ollama Recomendados

```bash
# Modelos ligeros (< 4GB RAM)
ollama pull llama3.2:1b
ollama pull phi3:mini

# Modelos estándar (8GB RAM)
ollama pull llama3.2
ollama pull mistral

# Modelos avanzados (16GB+ RAM)
ollama pull llama3.1:70b
ollama pull codellama:34b
```

## 🐛 Troubleshooting

### Problema: "Error conectando con Ollama"

**Solución:**
```bash
# Verificar que Ollama esté ejecutándose
ollama list

# Reiniciar Ollama
ollama serve

# Verificar conectividad desde Docker
docker exec logistics_backend curl http://host.docker.internal:11434/api/tags
```

### Problema: "OpenAI API Key inválida"

**Solución:**
```bash
# Verificar la clave
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Regenerar clave en https://platform.openai.com/api-keys
```

### Problema: "Frontend no se conecta al backend"

**Solución:**
```bash
# Verificar que ambos contenedores estén ejecutándose
docker ps

# Verificar logs
docker logs logistics_backend
docker logs logistics_frontend

# Reiniciar servicios
docker-compose restart
```

### Problema: "Optimización muy lenta"

**Soluciones:**
1. **Usar modelo más ligero:**
   ```bash
   # En .env
   OLLAMA_MODEL=llama3.2:1b
   ```

2. **Cambiar a OpenAI:**
   ```bash
   # En .env
   LLM_PROVIDER=openai
   ```

3. **Usar solo algoritmo básico:**
   - Comentar `OPENAI_API_KEY` en `.env`
   - El sistema usará automáticamente el algoritmo básico

## 📊 Monitoreo y Logs

### Verificar Estado del Sistema

```bash
# Estado general
curl http://localhost:8000/health

# Estado de IA
curl http://localhost:8000/llm-status

# Información del servidor
curl http://localhost:8000/
```

### Logs en Tiempo Real

```bash
# Backend
docker logs -f logistics_backend

# Frontend
docker logs -f logistics_frontend

# Ambos servicios
docker-compose logs -f
```

### Métricas de Rendimiento

```bash
# Tiempo de respuesta
time curl -X POST http://localhost:8000/api/optimize-routes \
  -H "Content-Type: application/json" \
  -d '{"deliveries":[{"id":"d1","weight":10}],"fleet":[{"id":"v1","capacity":20}]}'
```

## 🔄 Desarrollo Local

### Sin Docker

```bash
# Backend
cd crewai_backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (nueva terminal)
cd frontend
npm install
npm start
```

### Con Hot Reload

```bash
# Modificar docker-compose.yml para desarrollo
# Agregar volúmenes para hot reload
```

## 🚀 Despliegue en Producción

### Consideraciones

1. **Usar OpenAI en producción** (más estable que Ollama)
2. **Configurar límites de recursos** en Docker
3. **Implementar load balancer** para múltiples instancias
4. **Monitoreo con Prometheus/Grafana**
5. **Logs centralizados con ELK Stack**

### Variables de Producción

```bash
# .env.production
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-prod-key-here
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs`
2. Verifica la configuración: `curl http://localhost:8000/llm-status`
3. Consulta la documentación de la API: `http://localhost:8000/docs`
4. Abre un issue en el repositorio con los logs relevantes