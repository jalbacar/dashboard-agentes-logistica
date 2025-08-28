# crewai_backend/Dockerfile

# 1. Usar una imagen base de Python
FROM python:3.11-slim

# 2. Establecer el directorio de trabajo
WORKDIR /app

# 3. Copiar el archivo de dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el resto de los archivos de la aplicación
COPY . .

# 5. Exponer el puerto en el que correrá la API
EXPOSE 8000

# 6. Comando para iniciar el servidor de FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
