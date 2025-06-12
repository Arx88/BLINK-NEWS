# Guía de Uso: News Blink

Esta guía proporciona instrucciones detalladas para configurar, ejecutar y entender la aplicación News Blink, un sistema automatizado que busca, resume y presenta noticias notables en formato de 'blinks'.

## 1. Estructura del Proyecto

El proyecto News Blink está dividido en dos componentes principales:

-   **`news-blink-backend`**: Contiene la lógica del servidor, la recolección de noticias, el procesamiento y la generación de blinks. Está desarrollado en Python utilizando Flask.
-   **`news-blink-frontend`**: Contiene la interfaz de usuario, desarrollada con React y Vite.

```
news-blink-project/
├── news-blink-backend/
│   ├── src/
│   │   ├── data/             # Almacena noticias crudas y blinks generados
│   │   ├── database/         # Base de datos SQLite (app.db)
│   │   ├── models/           # Modelos de datos y lógica de negocio (scrapers, generadores)
│   │   ├── routes/           # Endpoints de la API Flask
│   │   ├── static/           # Archivos estáticos del backend (ej. index.html)
│   │   ├── utils/            # Utilidades varias
│   │   └── app.py            # Aplicación principal Flask
│   │   └── requirements.txt  # Dependencias de Python
│   └── .git/                 # Repositorio Git
├── news-blink-frontend/
│   ├── public/               # Archivos estáticos públicos
│   ├── src/                  # Código fuente de React
│   │   ├── assets/           # Activos (imágenes, etc.)
│   │   ├── components/       # Componentes de React (incluyendo componentes UI de Shadcn/ui)
│   │   ├── hooks/            # Hooks personalizados de React
│   │   ├── lib/              # Utilidades de frontend
│   │   ├── App.jsx           # Componente principal de la aplicación
│   │   ├── index.css         # Estilos globales
│   │   └── main.jsx          # Punto de entrada de la aplicación
│   ├── package.json          # Dependencias de Node.js y scripts
│   ├── vite.config.js        # Configuración de Vite
│   └── ...
├── setup.py                  # Script de instalación para el backend
├── README.md                 # Esta guía de uso
└── analisis_funcionalidades.md # Análisis de funcionalidades (proporcionado por el usuario)
```

## 2. Configuración e Instalación

Para poner en marcha la aplicación News Blink, sigue los siguientes pasos:

### 2.1. Ollama (Servidor de Modelos de Lenguaje)

Para que el backend pueda generar resúmenes con IA, necesitarás tener Ollama instalado y ejecutándose en tu sistema. Sigue estos pasos:

1.  **Descarga e instala Ollama:**
    Visita el sitio web oficial de Ollama: `https://ollama.com/` y descarga el instalador para tu sistema operativo (Windows, macOS, Linux). Sigue las instrucciones de instalación.

2.  **Inicia el servidor de Ollama:**
    Una vez instalado, Ollama se ejecutará automáticamente en segundo plano. Puedes verificar su estado abriendo una terminal y ejecutando:
    ```bash
    ollama list
    ```
    Si no ves nada, significa que no hay modelos descargados aún.

3.  **Descarga un modelo de lenguaje:**
    Para la generación de resúmenes, se recomienda un modelo como `llama3`. Descárgalo ejecutando en tu terminal:
    ```bash
    ollama pull llama3
    ```
    Este proceso puede tardar un tiempo dependiendo de tu conexión a internet y el tamaño del modelo. Asegúrate de que el modelo `llama3` esté disponible, ya que el código del backend está configurado para usarlo por defecto.

### 2.2. Backend (Python)

1.  **Navega al directorio raíz del proyecto:**
    ```bash
    cd /home/ubuntu/news-blink-app/news-blink-project
    ```
2.  **Instala las dependencias del backend:**
    Hemos proporcionado un archivo `setup.py` para simplificar la instalación de las dependencias de Python. Ejecuta el siguiente comando:
    ```bash
    pip install .
    ```
    Esto instalará Flask, Flask-CORS, requests, beautifulsoup4, nltk y la librería `ollama` para Python, y configurará el backend como un paquete Python.

### 2.3. Frontend (Node.js/React)

1.  **Navega al directorio del frontend:**
    ```bash
    cd /home/ubuntu/news-blink-app/news-blink-project/news-blink-frontend
    ```
2.  **Instala `pnpm` (si no lo tienes):**
    El proyecto utiliza `pnpm` como gestor de paquetes. Si no lo tienes instalado globalmente, puedes instalarlo con npm:
    ```bash
    npm install -g pnpm
    ```
3.  **Instala las dependencias del frontend:**
    ```bash
    pnpm install
    ```

## 3. Ejecución de la Aplicación

Para ejecutar la aplicación News Blink, deberás iniciar tanto el backend como el frontend por separado.

### 3.1. Iniciar el Backend

1.  **Asegúrate de que Ollama esté corriendo y el modelo `llama3` esté descargado.**
2.  **Asegúrate de estar en el directorio `src` del backend:**
    ```bash
    cd /home/ubuntu/news-blink-app/news-blink-project/news-blink-backend/src
    ```
3.  **Ejecuta la aplicación Flask:**
    ```bash
    python3 app.py
    ```
    El backend se iniciará y estará disponible en `http://127.0.0.1:5000` (o el puerto configurado). La base de datos `app.db` se creará automáticamente si no existe.

### 3.2. Iniciar el Frontend

1.  **Asegúrate de estar en el directorio raíz del frontend:**
    ```bash
    cd /home/ubuntu/news-blink-app/news-blink-project/news-blink-frontend
    ```
2.  **Ejecuta la aplicación React con Vite:**
    ```bash
    pnpm run dev
    ```
    El frontend se iniciará y se abrirá automáticamente en tu navegador predeterminado (generalmente `http://localhost:5173/` o un puerto similar). Asegúrate de que el backend esté corriendo para que el frontend pueda obtener los datos.

## 4. Funcionalidades Clave

### 4.1. Recolección y Procesamiento de Noticias con IA

El backend de News Blink es responsable de:

-   **Búsqueda de Noticias:** Busca en internet las noticias más notables de las últimas 24 horas.
-   **Recolección de Múltiples Fuentes:** Recopila información de diversas fuentes para construir una noticia más completa y objetiva.
-   **Generación de Blinks con IA:** Utiliza Ollama para sintetizar la noticia consolidada y generar un "blink", que es un resumen conciso en formato de caja con una imagen y 5 puntos clave (bullets) generados por IA.

### 4.2. Sistema de Votación de Blinks

La aplicación incluye un sistema de votación sencillo para los blinks. Los usuarios pueden interactuar con los blinks votando a favor o en contra, lo que permite una curación de contenido por parte de la comunidad.

### 4.3. Interfaz de Usuario (Frontend)

El frontend, desarrollado con React, proporciona una interfaz intuitiva para:

-   Visualizar los blinks generados.
-   Interactuar con el sistema de votación.
-   Explorar los detalles de cada noticia.

## 5. Notas Adicionales

-   **Base de Datos:** El backend utiliza una base de datos SQLite (`app.db`) para almacenar la información de las noticias y los blinks. Esta base de datos se creará automáticamente la primera vez que se ejecute el backend.
-   **Personalización:** Puedes explorar el código fuente en los directorios `news-blink-backend/src` y `news-blink-frontend/src` para personalizar la lógica de recolección de noticias, los algoritmos de resumen o la interfaz de usuario.
-   **Despliegue:** Para un despliegue en producción, se recomienda utilizar un servidor web como Gunicorn o uWSGI para el backend de Flask y un servidor como Nginx o Apache para servir los archivos estáticos del frontend.


