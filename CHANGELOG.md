# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

## [3.0.0] - 2024-12-19

### 🚀 Nuevas Características
- **Soporte para Ollama**: Modelos de IA locales y gratuitos
- **Configuración flexible**: Cambio dinámico entre OpenAI y Ollama
- **Fallback automático**: Si falla la IA, usa algoritmo básico
- **Endpoint de estado**: `/llm-status` para monitorear configuración de IA
- **Validación mejorada**: Validación robusta de datos de entrada
- **Respuestas enriquecidas**: Información sobre método de optimización usado

### 🔧 Mejoras
- **Manejo de errores mejorado**: Mejor gestión de fallos de IA
- **Logs más informativos**: Información detallada sobre el proceso
- **Configuración Docker optimizada**: Soporte para `host.docker.internal`
- **Documentación completa**: README actualizado y guía de instalación

### 🐛 Correcciones
- Corrección en la configuración de CORS
- Mejor manejo de timeouts en requests a LLM
- Validación de capacidad y peso siempre positivos

### 📦 Dependencias
- `langchain-ollama==0.1.3`: Soporte para Ollama
- `langchain-openai==0.1.25`: Soporte para OpenAI
- Actualización de FastAPI y Pydantic

## [2.0.0] - 2024-12-18

### 🚀 Nuevas Características
- **Backend FastAPI completo**: API REST funcional
- **Frontend React interactivo**: Dashboard con comunicación real
- **Containerización Docker**: Configuración completa con Docker Compose
- **Algoritmo de optimización**: Asignación básica de entregas a vehículos

### 🔧 Mejoras
- Proxy configurado en frontend para comunicación con backend
- Estilos CSS mejorados y responsive
- Manejo de estados de carga y errores

## [1.0.0] - 2024-12-17

### 🚀 Lanzamiento Inicial
- **Estructura base del proyecto**: Carpetas frontend y backend
- **Configuración inicial**: Docker y Docker Compose básico
- **README inicial**: Documentación básica del proyecto

---

## Formato

Este changelog sigue el formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere al [Versionado Semántico](https://semver.org/lang/es/).

### Tipos de cambios
- `🚀 Nuevas Características` para nuevas funcionalidades
- `🔧 Mejoras` para cambios en funcionalidades existentes
- `🐛 Correcciones` para corrección de bugs
- `📦 Dependencias` para cambios en dependencias
- `🔒 Seguridad` para vulnerabilidades corregidas
- `⚠️ Deprecado` para funcionalidades que serán removidas
- `❌ Removido` para funcionalidades removidas