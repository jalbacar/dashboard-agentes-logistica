# frontend/Dockerfile

FROM node:18-alpine

WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm ci --only=production=false

# Copiar el resto de los archivos
COPY . .

# Exponer puerto
EXPOSE 3000

# Iniciar aplicación
CMD ["sh", "-c", "HOST=0.0.0.0 npm start"]
