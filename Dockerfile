# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar las dependencias del sistema necesarias en una sola capa para optimizar
# Se añade 'gnupg' que es requerido por 'apt-key'
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome y Chromedriver
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb || apt-get install -f -y \
    && rm google-chrome-stable_current_amd64.deb

# Copiar el archivo de dependencias primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto al contenedor
COPY . .

# Exponer el puerto en el que corre Flask
EXPOSE 5000

# Comando para ejecutar la aplicación cuando se inicie el contenedor
CMD ["python", "start.py"]