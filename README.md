# Dashboard de Agentes de Logística

Sistema de optimización de rutas logísticas usando agentes de IA con FastAPI y React.

## 🚀 Características

- **Backend FastAPI**: API REST para optimización de rutas
- **Frontend React**: Dashboard interactivo con TypeScript
- **Containerización**: Docker y Docker Compose
- **Optimización**: Algoritmo de asignación de entregas a vehículos

## 📋 Requisitos

- Docker
- Docker Compose

## 🛠️ Instalación y Uso

1. **Clonar el repositorio**
```bash
git clone <tu-repo-url>
cd proyecto_logista_v1
```

2. **Ejecutar con Docker Compose**
```bash
docker-compose up -d --build
```

3. **Acceder a la aplicación**
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

- `POST /api/optimize-routes` - Optimizar rutas de entrega
- `GET /health` - Estado del servicio
- `GET /` - Información del servidor

## 🐳 Docker

El proyecto incluye configuración completa de Docker:
- **Frontend**: Node.js 18 Alpine
- **Backend**: Python 3.11 Slim
- **Red**: Comunicación entre contenedores

## 📝 Ejemplo de Uso

```json
POST /api/optimize-routes
{
  "deliveries": [
    {"id": "d1", "weight": 10},
    {"id": "d2", "weight": 25}
  ],
  "fleet": [
    {"id": "v1", "capacity": 35}
  ]
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