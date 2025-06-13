# Dockerfile

# Usar una imagen oficial de Python como base, una versión completa en lugar de 'slim'
# para tener más librerías base disponibles.
FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# --- INSTALACIÓN ROBUSTA DE DEPENDENCIAS DEL SISTEMA Y CHROME ---
# Actualizar, instalar herramientas y luego las librerías requeridas por Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    # Librerías esenciales para que Chrome/Chromedriver funcione
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libdbus-1-3 \
    libxtst6 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    # Limpiar al final para mantener la imagen ligera
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar la clave de Google y Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# --- INSTALACIÓN DE DEPENDENCIAS DE PYTHON ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 5000

# Comando de inicio
CMD ["python", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]