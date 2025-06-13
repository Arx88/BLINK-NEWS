# routes/topic_search.py

from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime
import threading
import time
import hashlib
from models.news_agent import crear_agente_de_noticias

topic_search_bp = Blueprint('topic_search', __name__)
active_searches = {}

# --- HELPER FUNCTIONS ---
def _get_results_filepath(search_key):
    """Construye la ruta al archivo de resultados para una búsqueda."""
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'topic_searches')
    return os.path.join(results_dir, f"search_{search_key}.json")

def _save_search_results(search_key, results):
    """Guarda los resultados de una búsqueda en un archivo JSON."""
    filepath = _get_results_filepath(search_key)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
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
    """Inicia una nueva búsqueda por tema, limpiando cualquier resultado anterior."""
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

    # Borrar resultados viejos antes de empezar
    _delete_search_results(search_key)

    active_searches[search_key] = {
        'topic': topic, 'started_at': datetime.now().isoformat(), 'status': 'starting'
    }

    threading.Thread(
        target=process_topic_search,
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
    """Obtiene el estado de una búsqueda. Lógica corregida para perfecta sincronización."""
    if search_key in active_searches:
        # La tarea está activa. Devolver su estado actual.
        return jsonify(active_searches[search_key])
    else:
        # La tarea NO está activa. Significa que ha terminado o nunca existió.
        # Ahora sí, buscamos el archivo de resultados.
        results = _get_search_results(search_key)
        if results:
            # Se encontró un archivo, la tarea está completada.
            return jsonify({'status': 'completed', 'results': results})
        else:
            # No está activa y no hay archivo. La búsqueda no se encuentra.
            return jsonify({'status': 'not_found', 'message': 'Búsqueda no encontrada o expirada.'}), 404

# --- BACKGROUND PROCESS ---
def process_topic_search(topic, hours_back, max_sources, search_key):
    """Procesa la búsqueda en segundo plano y limpia el estado al finalizar."""
    try:
        print(f"🤖 Agente de IA iniciando investigación para el tema: {topic}")
        active_searches[search_key]['status'] = 'generating_notes'

        agent_executor = crear_agente_de_noticias()
        prompt_para_agente = f"Investiga a fondo y redacta una nota periodística completa y objetiva sobre '{topic}', basándote en noticias de las últimas {hours_back} horas."
        resultado_agente = agent_executor.invoke({"input": prompt_para_agente})

        nota_generada = resultado_agente.get('output', 'El agente no pudo generar una nota.')

        superior_note = {
            'id': hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest(),
            'topic': topic,
            'title': f"Análisis Autónomo sobre: {topic}",
            'full_content': nota_generada,
            'ultra_summary': [], # Se puede mejorar para que el agente los genere
            'sources': ["Agente de IA con Tavily Search"], 'urls': [], 'articles_count': "Varias",
            'timestamp': datetime.now().isoformat(), 'image': None,
        }

        results = {
            'status': 'success', 'topic': topic, 'superior_notes': [superior_note],
            'total_groups_found': 1, 'notes_generated': 1, 'timestamp': datetime.now().isoformat()
        }
        _save_search_results(search_key, results)
        print(f"✅ Investigación del agente completada para el tema: {topic}")

    except Exception as e:
        print(f"❌ Error en el proceso del agente de IA: {e}")
        _save_search_results(search_key, {
            'status': 'error', 'message': f'Error procesando búsqueda: {str(e)}',
            'topic': topic, 'timestamp': datetime.now().isoformat()
        })
    finally:
        # --- LA SOLUCIÓN CLAVE ---
        # Al finalizar (con éxito o error), se elimina la tarea de la lista de activas.
        if search_key in active_searches:
            del active_searches[search_key]
            print(f"La búsqueda '{search_key}' ha sido marcada como finalizada.")
