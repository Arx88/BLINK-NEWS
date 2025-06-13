# Dockerfile

# Usamos una imagen base de Debian (Bookworm) completa para máxima compatibilidad
FROM python:3.11-bookworm

# Variable de entorno para instalaciones no interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema robustas
# Incluye todas las librerías conocidas para Chrome y un 'display' virtual (xvfb)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libdbus-1-3 \
    libxtst6 \
    libxss1 \
    libxrandr2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    # Limpiar caché para mantener la imagen pequeña
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y \
    && rm google-chrome-stable_current_amd64.deb

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto de Flask
EXPOSE 5000

# --- COMANDO DE INICIO A PRUEBA DE BALAS ---
# Ejecutar la aplicación dentro del display virtual 'xvfb'
CMD ["xvfb-run", "--auto-servernum", "python", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]