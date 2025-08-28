# Guía de Contribución

¡Gracias por tu interés en contribuir al Dashboard de Agentes de Logística! 🚀

## 🤝 Cómo Contribuir

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/proyecto_logista_v1.git
cd proyecto_logista_v1
```

### 2. Configurar Entorno de Desarrollo

```bash
# Copiar configuración
cp .env.example .env

# Configurar para desarrollo (recomendado Ollama)
echo "LLM_PROVIDER=ollama" >> .env

# Instalar Ollama y modelo
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

### 3. Crear Rama de Feature

```bash
# Crear rama desde main
git checkout -b feature/nombre-de-tu-feature

# O para bugfixes
git checkout -b fix/descripcion-del-bug
```

### 4. Desarrollo

```bash
# Ejecutar en modo desarrollo
docker-compose up -d --build

# Verificar que todo funciona
curl http://localhost:8000/llm-status
curl http://localhost:3000
```

## 📋 Estándares de Código

### Backend (Python/FastAPI)

- **Estilo**: Seguir PEP 8
- **Tipo de hints**: Usar type hints en todas las funciones
- **Documentación**: Docstrings para funciones públicas
- **Validación**: Usar Pydantic para validación de datos

```python
# Ejemplo de función bien documentada
async def optimize_routes(
    deliveries: List[DeliveryItem], 
    fleet: List[VehicleItem]
) -> OptimizationResult:
    """
    Optimiza rutas usando IA o algoritmo básico.
    
    Args:
        deliveries: Lista de entregas a asignar
        fleet: Lista de vehículos disponibles
        
    Returns:
        Resultado de optimización con rutas asignadas
    """
    pass
```

### Frontend (React/TypeScript)

- **Estilo**: Usar TypeScript estricto
- **Componentes**: Componentes funcionales con hooks
- **Naming**: PascalCase para componentes, camelCase para variables
- **Props**: Definir interfaces para props

```typescript
// Ejemplo de componente bien tipado
interface RouteCardProps {
  route: OptimizedRoute;
  onEdit?: (routeId: string) => void;
}

const RouteCard: React.FC<RouteCardProps> = ({ route, onEdit }) => {
  // Implementación
};
```

## 🧪 Testing

### Backend Tests

```bash
# Ejecutar tests del backend
cd crewai_backend
python -m pytest tests/ -v

# Con coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests

```bash
# Ejecutar tests del frontend
cd frontend
npm test

# Tests con coverage
npm test -- --coverage --watchAll=false
```

## 📝 Commits

### Formato de Commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(scope): descripción corta

Descripción más detallada si es necesaria.

Fixes #123
```

### Tipos de Commits

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan funcionalidad)
- `refactor`: Refactoring de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

### Ejemplos

```bash
# Nueva funcionalidad
git commit -m "feat(backend): agregar soporte para múltiples modelos Ollama"

# Corrección de bug
git commit -m "fix(frontend): corregir error de conexión con backend"

# Documentación
git commit -m "docs: actualizar guía de instalación con Ollama"
```

## 🔍 Pull Request

### Antes de Enviar

1. **Tests**: Asegurar que todos los tests pasan
2. **Linting**: Código sin errores de linting
3. **Documentación**: Actualizar documentación si es necesario
4. **Changelog**: Agregar entrada en CHANGELOG.md

### Checklist del PR

- [ ] Tests pasan localmente
- [ ] Código sigue los estándares del proyecto
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado
- [ ] Descripción clara del cambio
- [ ] Screenshots si hay cambios visuales

### Template del PR

```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva funcionalidad (cambio que agrega funcionalidad)
- [ ] Breaking change (cambio que rompe compatibilidad)
- [ ] Documentación

## Testing
- [ ] Tests unitarios agregados/actualizados
- [ ] Tests de integración verificados
- [ ] Probado manualmente

## Screenshots (si aplica)
Agregar screenshots de cambios visuales.
```

## 🐛 Reportar Bugs

### Información Necesaria

1. **Descripción**: Qué esperabas vs qué pasó
2. **Pasos para reproducir**: Lista detallada
3. **Entorno**: OS, versión de Docker, configuración
4. **Logs**: Logs relevantes del error
5. **Screenshots**: Si es un error visual

### Template de Issue

```markdown
**Descripción del Bug**
Descripción clara del problema.

**Pasos para Reproducir**
1. Ir a '...'
2. Hacer click en '...'
3. Ver error

**Comportamiento Esperado**
Qué debería pasar.

**Screenshots**
Si aplica, agregar screenshots.

**Entorno:**
- OS: [e.g. Windows 10, macOS, Ubuntu]
- Docker: [e.g. 20.10.8]
- LLM Provider: [e.g. ollama, openai]
- Versión: [e.g. 3.0.0]

**Logs**
```
Pegar logs relevantes aquí
```
```

## 💡 Sugerir Funcionalidades

### Template de Feature Request

```markdown
**¿Tu feature request está relacionado con un problema?**
Descripción clara del problema.

**Describe la solución que te gustaría**
Descripción clara de lo que quieres que pase.

**Describe alternativas que has considerado**
Otras soluciones o funcionalidades consideradas.

**Contexto adicional**
Cualquier otro contexto o screenshots.
```

## 🏗️ Arquitectura del Proyecto

### Estructura de Carpetas

```
proyecto_logista_v1/
├── crewai_backend/          # API FastAPI
│   ├── main.py             # Punto de entrada
│   ├── models/             # Modelos Pydantic
│   ├── services/           # Lógica de negocio
│   ├── utils/              # Utilidades
│   └── tests/              # Tests del backend
├── frontend/               # App React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── services/       # Servicios API
│   │   ├── types/          # Tipos TypeScript
│   │   └── utils/          # Utilidades
│   └── tests/              # Tests del frontend
├── docs/                   # Documentación adicional
└── scripts/                # Scripts de utilidad
```

### Principios de Diseño

1. **Separación de responsabilidades**: Backend y frontend independientes
2. **Configuración flexible**: Soporte para múltiples proveedores de IA
3. **Fallback robusto**: Siempre tener un plan B
4. **Containerización**: Todo debe funcionar en Docker
5. **Documentación**: Código autodocumentado

## 📞 Contacto

- **Issues**: Para bugs y feature requests
- **Discussions**: Para preguntas generales
- **Email**: Para temas sensibles

¡Gracias por contribuir! 🎉