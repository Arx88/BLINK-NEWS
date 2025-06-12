# Diseño de Arquitectura - News Blink Mejorado

## Análisis del Proyecto Base

El proyecto actual tiene:
- Sistema de scraping de múltiples fuentes (El País, ABC, Xataka, etc.)
- Generación de BLINKs usando OLLAMA con modelo llama3
- Frontend React con interfaz moderna
- Backend Flask con API REST
- Sistema de agrupación de noticias similares

## Nuevas Funcionalidades Requeridas

### 1. Búsqueda por Tema Específico
- **Entrada**: Tema específico (ej: "Argentina")
- **Proceso**: Buscar noticias relacionadas en las últimas 24 horas
- **Salida**: Lista de noticias relevantes al tema

### 2. Recopilación de Múltiples Fuentes
- **Entrada**: Noticia principal identificada
- **Proceso**: Buscar la misma noticia en 3-5 fuentes diferentes
- **Salida**: Conjunto de artículos sobre el mismo evento

### 3. Generación de NOTA SUPERIOR
- **Entrada**: 3-5 artículos sobre el mismo tema
- **Proceso**: Usar OLLAMA para crear una nota comprehensiva con múltiples puntos de vista
- **Salida**: Artículo completo con análisis de todas las fuentes

### 4. ULTRA RESUMEN IA
- **Entrada**: NOTA SUPERIOR
- **Proceso**: Generar 5 bullets con lo más importante
- **Salida**: Resumen ultra breve para lectura rápida

## Modificaciones Necesarias

### Backend (Flask)

#### 1. Nuevo Endpoint de Búsqueda por Tema
```python
@app.route('/api/search-topic', methods=['POST'])
def search_topic():
    # Recibe tema y busca noticias relevantes
    pass
```

#### 2. Modificación del Scraper
- Agregar método `search_by_topic(topic, hours=24)`
- Implementar búsqueda en múltiples fuentes para el mismo evento
- Mejorar algoritmo de similitud para agrupar noticias del mismo evento

#### 3. Nuevo Generador de Notas Superiores
```python
class SuperiorNoteGenerator:
    def generate_superior_note(self, articles_group):
        # Usar OLLAMA para crear nota comprehensiva
        pass
    
    def generate_ultra_summary(self, superior_note):
        # Generar 5 bullets principales
        pass
```

#### 4. Nuevos Modelos de Datos
```python
class SuperiorNote:
    - id
    - topic
    - title
    - full_content (NOTA SUPERIOR)
    - ultra_summary (5 bullets)
    - sources (3-5 fuentes)
    - timestamp
    - original_articles
```

### Frontend (React)

#### 1. Nueva Página de Búsqueda por Tema
- Input para ingresar tema
- Botón de búsqueda
- Loading state durante procesamiento

#### 2. Componente de Nota Superior
- Vista de ULTRA RESUMEN (5 bullets)
- Botón "VER NOTA COMPLETA"
- Modal o página expandida para nota completa
- Lista de fuentes utilizadas

#### 3. Modificación de la Navegación
- Agregar nueva sección "Búsqueda por Tema"
- Mantener funcionalidad existente

## Flujo de Trabajo Propuesto

### 1. Usuario Ingresa Tema
```
Usuario → Input "Argentina" → Click "Buscar"
```

### 2. Búsqueda y Recopilación
```
Backend → Buscar "Argentina" en últimas 24h → Encontrar noticias relevantes
       → Para cada noticia importante → Buscar en 3-5 fuentes diferentes
       → Agrupar artículos del mismo evento
```

### 3. Procesamiento con IA
```
OLLAMA → Recibir 3-5 artículos del mismo evento
       → Generar NOTA SUPERIOR con múltiples puntos de vista
       → Extraer 5 bullets más importantes
```

### 4. Presentación al Usuario
```
Frontend → Mostrar ULTRA RESUMEN (5 bullets)
         → Botón "VER NOTA COMPLETA"
         → Modal con nota completa y fuentes
```

## Integración con Sistema Existente

### Reutilización de Componentes
- **Scraper existente**: Extender para búsqueda por tema
- **BlinkGenerator**: Adaptar para generar notas superiores
- **Frontend**: Agregar nuevos componentes sin romper existentes
- **API**: Mantener endpoints actuales, agregar nuevos

### Nuevas Dependencias
- Mejorar prompts de OLLAMA para análisis multi-fuente
- Implementar algoritmo de detección de eventos similares
- Agregar sistema de ranking de importancia de noticias

## Estructura de Archivos Modificada

```
news-blink-backend/src/
├── models/
│   ├── scraper.py (modificado)
│   ├── blink_generator.py (modificado)
│   ├── superior_note_generator.py (nuevo)
│   └── topic_searcher.py (nuevo)
├── routes/
│   ├── api.py (modificado)
│   └── topic_search.py (nuevo)
└── data/
    ├── superior_notes/ (nuevo)
    └── topic_searches/ (nuevo)

news-blink-frontend/src/
├── components/
│   ├── TopicSearch.jsx (nuevo)
│   ├── SuperiorNote.jsx (nuevo)
│   └── UltraSummary.jsx (nuevo)
└── pages/
    └── TopicSearchPage.jsx (nuevo)
```

## Consideraciones Técnicas

### Performance
- Cache de búsquedas recientes
- Procesamiento asíncrono para búsquedas largas
- Límite de fuentes para evitar sobrecarga

### UX/UI
- Loading states claros durante procesamiento
- Indicadores de progreso
- Manejo de errores amigable

### Escalabilidad
- Sistema modular para agregar nuevas fuentes
- Configuración flexible de modelos OLLAMA
- Base de datos para persistir búsquedas

