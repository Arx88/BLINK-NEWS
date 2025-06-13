# routes/topic_search.py

from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime
import threading
import time
import hashlib
from models.topic_searcher import TopicSearcher # ADD THIS
from models.superior_note_generator import SuperiorNoteGenerator # ADD THIS

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
    """
    Procesa la búsqueda en segundo plano utilizando TopicSearcher y SuperiorNoteGenerator,
    y limpia el estado al finalizar.
    """
    try:
        # 1. Instanciar los modelos correctos
        searcher = TopicSearcher()
        note_generator = SuperiorNoteGenerator()

        # 2. Actualizar estado e iniciar la búsqueda de noticias agrupadas
        print(f"🔎 Iniciando búsqueda y agrupación de noticias para: '{topic}'")
        active_searches[search_key]['status'] = 'searching_news'

        # El método search_topic_news ya busca y agrupa las noticias por evento
        grouped_news = searcher.search_topic_news(
            topic=topic,
            hours_back=hours_back,
            max_sources=max_sources
        )

        if not grouped_news:
            print(f"🟡 No se encontraron grupos de noticias para '{topic}'.")
            results = {
                'status': 'no_results',
                'message': 'No se encontraron suficientes noticias de múltiples fuentes sobre este tema en el período de tiempo seleccionado.',
                'topic': topic,
                'superior_notes': [],
                'total_groups_found': 0,
                'notes_generated': 0,
                'timestamp': datetime.now().isoformat()
            }
            _save_search_results(search_key, results)
            return # Termina la ejecución del hilo

        # 3. Actualizar estado y comenzar la generación de notas
        print(f"🧠 Encontrados {len(grouped_news)} grupos de noticias. Iniciando generación de Notas Superiores.")
        active_searches[search_key]['status'] = 'generating_notes'

        all_superior_notes = []
        for i, group in enumerate(grouped_news):
            print(f"--- Procesando grupo {i+1}/{len(grouped_news)} ---")
            try:
                # 4. Generar una Nota Superior para cada grupo de artículos
                # Este método ya incluye la creación de la nota y el ultra resumen
                superior_note = note_generator.generate_superior_note(group, topic)
                all_superior_notes.append(superior_note)
            except Exception as e:
                print(f"Error generando nota para el grupo {i+1}: {e}")
                continue # Si un grupo falla, continúa con el siguiente

        # 5. Ensamblar y guardar los resultados finales
        print(f"✅ Proceso completado. Se generaron {len(all_superior_notes)} Notas Superiores.")
        final_results = {
            'status': 'success',
            'topic': topic,
            'superior_notes': all_superior_notes,
            'total_groups_found': len(grouped_news),
            'notes_generated': len(all_superior_notes),
            'timestamp': datetime.now().isoformat()
        }
        _save_search_results(search_key, final_results)

    except Exception as e:
        print(f"❌ Error crítico en el proceso de búsqueda: {e}")
        error_results = {
            'status': 'error',
            'message': f'Error procesando la búsqueda: {str(e)}',
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        }
        _save_search_results(search_key, error_results)
    finally:
        # Limpiar la tarea de la lista de búsquedas activas para permitir nuevas búsquedas
        if search_key in active_searches:
            del active_searches[search_key]
            print(f"La búsqueda '{search_key}' ha sido marcada como finalizada.")
