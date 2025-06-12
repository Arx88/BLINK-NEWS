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
├── setup.py                  # Script de instalación unificado (backend y frontend)
├── start.py                  # Script para iniciar la aplicación completa (backend y frontend)
├── README.md                 # Esta guía de uso
└── analisis_funcionalidades.md # Análisis de funcionalidades (proporcionado por el usuario)
```

## 2. Configuración e Instalación

Para poner en marcha la aplicación News Blink, sigue los siguientes pasos:

### 2.1. Ollama (Servidor de Modelos de Lenguaje)

Es un **prerrequisito indispensable** tener Ollama instalado y ejecutándose en tu sistema para que el backend pueda generar resúmenes con IA.

1.  **Descarga e instala Ollama:**
    Visita el sitio web oficial de Ollama: `https://ollama.com/` y descarga el instalador para tu sistema operativo (Windows, macOS, Linux). Sigue las instrucciones de instalación.

2.  **Inicia el servidor de Ollama:**
    Una vez instalado, Ollama debería ejecutarse automáticamente. Puedes verificar su estado abriendo una terminal y ejecutando:
    ```bash
    ollama list
    ```
    Si no ves nada, significa que no hay modelos descargados aún.

3.  **Descarga un modelo de lenguaje:**
    Para la generación de resúmenes, se recomienda un modelo como `llama3`. Descárgalo ejecutando en tu terminal:
    ```bash
    ollama pull llama3
    ```
    Este proceso puede tardar un tiempo. Asegúrate de que el modelo `llama3` esté disponible, ya que el código del backend está configurado para usarlo por defecto.

### 2.2. Configuración del Backend (Python)

El backend de News Blink requiere Python y sus dependencias gestionadas a través de un entorno virtual.

1.  **Crea un entorno virtual:**
    Navega al directorio raíz del proyecto y ejecuta:
    ```bash
    python -m venv venv
    ```
    Esto creará una carpeta `venv` en el raíz del proyecto.

2.  **Activa el entorno virtual:**
    *   En macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   En Windows (Git Bash o similar):
        ```bash
        source venv/Scripts/activate
        ```
    *   En Windows (Command Prompt):
        ```bash
        .\venv\Scripts\activate
        ```
    Deberías ver `(venv)` al principio de tu prompt de terminal.

3.  **Instala las dependencias de Python:**
    Asegúrate de que tu entorno virtual esté activado. Luego, desde el directorio raíz del proyecto, ejecuta:
    ```bash
    pip install -r requirements.txt
    ```
    Alternativamente, si deseas que el comando `news-blink-backend` esté disponible directamente (por ejemplo, para desarrollo o si `start.py` lo utiliza preferentemente), puedes instalar el paquete en modo editable:
    ```bash
    pip install -e .
    ```
    Esto también instalará las dependencias listadas en `setup.py` (que son las mismas de `requirements.txt`).

### 2.3. Configuración del Frontend (Node.js/pnpm)

El frontend de News Blink está construido con React y Vite, y sus dependencias se gestionan con pnpm.

1.  **Prerrequisitos (Node.js y pnpm):**
    *   Asegúrate de tener Node.js instalado. Se recomienda usar un gestor de versiones como [nvm](https://github.com/nvm-sh/nvm) para instalar y gestionar Node.js.
    *   Instala pnpm. Si tienes Node.js v16.13 o posterior, puedes habilitar `corepack` (que viene con Node.js) y luego instalar pnpm:
        ```bash
        corepack enable
        corepack prepare pnpm@latest --activate
        ```
        Alternativamente, puedes instalar pnpm globalmente usando npm (que viene con Node.js):
        ```bash
        npm install -g pnpm
        ```
        Verifica la instalación con `pnpm --version`.

2.  **Instala las dependencias del frontend:**
    *   Navega al directorio del frontend:
        ```bash
        cd news-blink-frontend
        ```
    *   Instala las dependencias:
        ```bash
        pnpm install
        ```
    *   Regresa al directorio raíz del proyecto:
        ```bash
        cd ..
        ```

## 3. Ejecución de la Aplicación

**Importante:** Antes de ejecutar la aplicación, asegúrate de que tu entorno virtual de Python (creado en el paso 2.2) esté activado.

Una vez completada la configuración e instalación:

1.  **Asegúrate de que Ollama esté corriendo y el modelo `llama3` esté descargado y accesible.** (Ver sección 2.1).
2.  **Navega al directorio raíz del proyecto** (si no estás ya allí).
3.  **Ejecuta el script `start.py`:**
    Este script se encargará de iniciar tanto el servidor backend como el servidor de desarrollo del frontend de manera concurrente.
    ```bash
    python start.py
    ```
    o, si tienes múltiples versiones de Python:
    ```bash
    python3 start.py
    ```
    *   El **backend** (Flask) intentará iniciarse, generalmente en `http://127.0.0.1:5000`.
    *   El **frontend** (Vite) intentará iniciarse, generalmente en `http://localhost:5173/`.
    *   Podrás ver los logs de ambos procesos en la consola, prefijados con `[BACKEND]` o `[FRONTEND]`.
    *   Para detener ambos servicios, presiona `Ctrl+C` en la terminal donde se está ejecutando `start.py`.

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

-   **Base de Datos:** El backend utiliza una base de datos SQLite (`app.db` dentro de `news-blink-backend/src/database/`) para almacenar la información de las noticias y los blinks.
-   **Personalización:** Puedes explorar el código fuente en los directorios `news-blink-backend/src` y `news-blink-frontend/src` para personalizar la lógica de recolección de noticias, los algoritmos de resumen o la interfaz de usuario.
-   **Despliegue:** Para un despliegue en producción, se recomienda utilizar un servidor web como Gunicorn o uWSGI para el backend de Flask y un servidor como Nginx o Apache para servir los archivos estáticos del frontend.

```
