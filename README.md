# Dashboard de Agentes de Logística

Sistema de optimización de rutas logísticas usando agentes de IA con FastAPI y React.

## 🚀 Características

- **Backend FastAPI**: API REST para optimización de rutas con IA
- **Frontend React**: Dashboard interactivo con TypeScript
- **Containerización**: Docker y Docker Compose
- **IA Flexible**: Soporte para OpenAI GPT y Ollama (modelos locales)
- **Optimización Inteligente**: Algoritmo básico + optimización con LLM
- **Fallback Automático**: Si falla la IA, usa algoritmo básico

## 📋 Requisitos

- Docker
- Docker Compose
- **Opción A**: OpenAI API Key (para usar GPT)
- **Opción B**: Ollama instalado localmente (modelos gratuitos)

## 🛠️ Instalación y Uso

1. **Clonar el repositorio**
```bash
git clone <tu-repo-url>
cd proyecto_logista_v1
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env según tu preferencia:
# - Para OpenAI: LLM_PROVIDER=openai y OPENAI_API_KEY
# - Para Ollama: LLM_PROVIDER=ollama (gratuito)
```

3. **Ejecutar con Docker Compose**
```bash
docker-compose up -d --build
```

4. **Acceder a la aplicación**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## 🏗️ Estructura del Proyecto

```
proyecto_logista_v1/
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── App.tsx          # Componente principal
│   │   └── index.tsx        # Punto de entrada
│   ├── Dockerfile
│   └── package.json
├── crewai_backend/          # API FastAPI
│   ├── main.py              # Servidor principal
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml       # Configuración de contenedores
```

## 🔧 Desarrollo

### Backend
```bash
cd crewai_backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 📡 API Endpoints

- `POST /api/optimize-routes` - Optimizar rutas de entrega con IA
- `GET /health` - Estado del servicio
- `GET /llm-status` - Estado de la configuración de IA
- `GET /` - Información del servidor

## 🐳 Docker

El proyecto incluye configuración completa de Docker:
- **Frontend**: Node.js 18 Alpine con proxy al backend
- **Backend**: Python 3.11 Slim con soporte para Ollama
- **Red**: Comunicación entre contenedores
- **Ollama**: Acceso a host local via `host.docker.internal`

## 🔍 Monitoreo

```bash
# Verificar estado de la IA
curl http://localhost:8000/llm-status

# Logs del backend
docker logs logistics_backend

# Logs del frontend
docker logs logistics_frontend
```

## 🤖 Configuración de IA

### Opción 1: OpenAI (Recomendado para producción)
```bash
# En .env
LLM_PROVIDER=openai
OPENAI_API_KEY=tu-api-key-aqui
```

### Opción 2: Ollama (Gratuito, local)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.2

# En .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

## 📝 Ejemplo de Uso

```json
POST /api/optimize-routes
{
  "deliveries": [
    {"id": "d1", "weight": 10, "orderId": "o1"},
    {"id": "d2", "weight": 25, "orderId": "o2"}
  ],
  "fleet": [
    {"id": "v1", "capacity": 35, "type": "truck"}
  ]
}
```

**Respuesta:**
```json
{
  "optimizedRoutes": [
    {
      "routeId": "RUTA-123",
      "vehicleId": "v1",
      "stops": [{"id": "d1", "weight": 10}, {"id": "d2", "weight": 25}],
      "totalWeight": 35
    }
  ],
  "unassignedDeliveries": [],
  "optimization_method": "llm_openai",
  "llm_used": true,
  "message": "Optimización realizada con OPENAI"
}
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.