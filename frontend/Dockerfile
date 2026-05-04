# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Imagen Docker del frontend. Partes: base Node, instalacion de dependencias, copia del codigo y comando de desarrollo Next.js.

FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev"]
