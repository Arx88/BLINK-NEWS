# news-blink-backend/src/routes/topic_search.py
from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime
import threading
import hashlib

# Importaciones directas de Langchain en lugar del agente
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_ollama.llms import OllamaLLM

topic_search_bp = Blueprint('topic_search', __name__)
active_searches = {}

# --- HELPER FUNCTIONS ---
def _get_results_filepath(search_key):
    """Construye la ruta al archivo de resultados para una búsqueda."""
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'topic_searches')
    os.makedirs(results_dir, exist_ok=True)
    return os.path.join(results_dir, f"search_{search_key}.json")

def _save_search_results(search_key, results):
    """Guarda los resultados de una búsqueda en un archivo JSON."""
    filepath = _get_results_filepath(search_key)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Resultados de búsqueda guardados: {filepath}")
    except Exception as e:
        print(f"Error guardando resultados de búsqueda: {e}")

def _get_search_results(search_key):
    """Obtiene los resultados de una búsqueda desde un archivo JSON."""
    filepath = _get_results_filepath(search_key)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error obteniendo resultados de búsqueda: {e}")
    return None

def _delete_search_results(search_key):
    """Elimina un archivo de resultados de búsqueda antiguo si existe."""
    filepath = _get_results_filepath(search_key)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Archivo de resultados antiguo eliminado: {filepath}")

# --- API ROUTES ---
@topic_search_bp.route('/search-topic', methods=['POST'])
def search_topic():
    data = request.get_json()
    if not data or 'topic' not in data or not data['topic'].strip():
        return jsonify({'error': 'Se requiere especificar un tema'}), 400

    topic = data['topic'].strip()
    hours_back = data.get('hours_back', 24)
    search_key = f"{topic.lower().replace(' ', '_')}_{hours_back}"

    if search_key in active_searches:
        return jsonify({
            'status': 'processing',
            'message': f'Búsqueda ya en progreso para "{topic}". Por favor espere...',
            'topic': topic
        })

    _delete_search_results(search_key)
    active_searches[search_key] = {
        'topic': topic, 'started_at': datetime.now().isoformat(), 'status': 'starting'
    }

    threading.Thread(
        target=process_topic_search_direct,
        args=(topic, hours_back, data.get('max_sources', 5), search_key),
        daemon=True
    ).start()

    return jsonify({
        'status': 'started',
        'message': f'Iniciando búsqueda para "{topic}". Esto puede tomar unos minutos...',
        'topic': topic,
        'search_key': search_key
    })

@topic_search_bp.route('/search-status/<search_key>', methods=['GET'])
def get_search_status(search_key):
    if search_key in active_searches:
        return jsonify(active_searches[search_key])
    else:
        results = _get_search_results(search_key)
        if results:
            return jsonify({'status': 'completed', 'results': results})
        else:
            return jsonify({'status': 'not_found', 'message': 'Búsqueda no encontrada o expirada.'}), 404

# --- BACKGROUND PROCESS (LÓGICA MEJORADA Y DIRECTA) ---
def process_topic_search_direct(topic, hours_back, max_sources, search_key):
    """Procesa la búsqueda de forma directa (sin agente) y limpia el estado al finalizar."""
    try:
        print(f"🤖 Iniciando investigación directa para el tema: {topic}")
        active_searches[search_key]['status'] = 'searching_news'

        # 1. Inicializar herramientas y LLM directamente
        tavily_search = TavilySearchResults(max_results=max_sources)
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        llm = OllamaLLM(model="qwen3:32b", base_url=ollama_base_url, temperature=0.3)

        # 2. Realizar la búsqueda de noticias
        print(f"-> Buscando en Tavily: 'noticias de {topic} en las últimas {hours_back} horas'")
        search_results = tavily_search.invoke(f"noticias de {topic} en las últimas {hours_back} horas")

        active_searches[search_key]['status'] = 'generating_notes'

        # 3. Crear un prompt específico para el LLM con el contexto de la búsqueda
        context = "## Contexto de Noticias Recientes:

"
        for result in search_results:
            context += f"- Fuente: {result.get('url')}
  Contenido: {result.get('content')}

"

        prompt_para_llm = f"""
Eres un periodista experto encargado de redactar un artículo objetivo y bien estructurado.
Basándote EXCLUSIVAMENTE en el siguiente contexto de noticias sobre "{topic}", redacta una nota periodística completa.

Instrucciones:
1.  **Encabezado y Estructura:** Crea un título principal para la nota. Estructura el contenido con subtítulos claros si es necesario.
2.  **Contenido:** Sintetiza la información de las distintas fuentes en un texto fluido y coherente. No inventes datos que no estén en el contexto. Si hay diferentes perspectivas, muéstralas.
3.  **Tono:** Mantén un tono neutral, profesional y periodístico.
4.  **No Incluir:** No menciones que eres una IA ni que te basas en un "contexto". Simplemente escribe el artículo como si fueras el autor.

{context}

Ahora, por favor, escribe la nota periodística completa sobre "{topic}":
        """

        # 4. Invocar el LLM para generar la nota
        print("-> Generando la nota periodística con el LLM...")
        nota_generada = llm.invoke(prompt_para_llm)

        # 5. Estructurar el resultado final
        superior_note = {
            'id': hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest(),
            'topic': topic,
            'title': f"Análisis sobre: {topic}",
            'full_content': nota_generada,
            'ultra_summary': [],
            'sources': [res.get('url') for res in search_results],
            'urls': [res.get('url') for res in search_results],
            'articles_count': len(search_results),
            'timestamp': datetime.now().isoformat(),
            'image': None,
        }

        results = {
            'status': 'success', 'topic': topic, 'superior_notes': [superior_note],
            'total_groups_found': 1, 'notes_generated': 1, 'timestamp': datetime.now().isoformat()
        }
        _save_search_results(search_key, results)
        print(f"✅ Investigación directa completada para el tema: {topic}")

    except Exception as e:
        print(f"❌ Error en el proceso de búsqueda directa: {e}")
        _save_search_results(search_key, {
            'status': 'error', 'message': f'Error procesando búsqueda: {str(e)}',
            'topic': topic, 'timestamp': datetime.now().isoformat()
        })
    finally:
        if search_key in active_searches:
            del active_searches[search_key]
            print(f"La búsqueda '{search_key}' ha sido marcada como finalizada.")
