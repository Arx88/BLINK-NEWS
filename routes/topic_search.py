# routes/topic_search.py
from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime
import threading
import hashlib
from models.topic_searcher import TopicSearcher
from models.superior_note_generator import SuperiorNoteGenerator

topic_search_bp = Blueprint('topic_search', __name__)
active_searches = {}

def _get_results_filepath(search_key):
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'topic_searches')
    os.makedirs(results_dir, exist_ok=True)
    return os.path.join(results_dir, f"search_{search_key}.json")

def _save_search_results(search_key, results):
    filepath = _get_results_filepath(search_key)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 Resultados de búsqueda guardados: {filepath}")
    except Exception as e:
        print(f"Error guardando resultados de búsqueda: {e}")

def _get_search_results(search_key):
    filepath = _get_results_filepath(search_key)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error obteniendo resultados de búsqueda: {e}")
    return None

def _delete_search_results(search_key):
    filepath = _get_results_filepath(search_key)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"🗑️ Archivo de resultados antiguo eliminado: {filepath}")

@topic_search_bp.route('/search-topic', methods=['POST'])
def search_topic():
    data = request.get_json()
    if not data or 'topic' not in data or not data['topic'].strip():
        return jsonify({'error': 'Se requiere especificar un tema'}), 400

    topic = data['topic'].strip()
    search_key = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest()

    if search_key in active_searches:
        return jsonify({'status': 'processing', 'message': f'Búsqueda ya en progreso para "{topic}". Por favor espere...','topic': topic})

    _delete_search_results(search_key)
    active_searches[search_key] = {'topic': topic, 'started_at': datetime.now().isoformat(), 'status': 'starting'}

    threading.Thread(
        target=process_topic_search,
        args=(topic, data.get('hours_back', 24), data.get('max_sources', 5), search_key),
        daemon=True
    ).start()

    return jsonify({'status': 'started', 'message': f'Iniciando búsqueda para "{topic}". Esto puede tomar unos minutos...','topic': topic, 'search_key': search_key})

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

def process_topic_search(topic, hours_back, max_sources, search_key):
    try:
        searcher = TopicSearcher()
        note_generator = SuperiorNoteGenerator()
        active_searches[search_key]['status'] = 'searching_news'
        grouped_news = searcher.search_topic_news(topic=topic, hours_back=hours_back, max_sources=max_sources)

        if not grouped_news:
            print(f"🟡 No se encontraron grupos de noticias para '{topic}'.")
            results = {'status': 'no_results', 'topic': topic, 'superior_notes': [], 'total_groups_found': 0, 'notes_generated': 0, 'message': 'No se encontraron suficientes noticias de múltiples fuentes sobre este tema.'}
            _save_search_results(search_key, results)
            return

        active_searches[search_key]['status'] = 'generating_notes'
        all_superior_notes = []
        for i, group in enumerate(grouped_news):
            print(f"--- Procesando grupo {i+1}/{len(grouped_news)} para generar Nota Superior ---")
            try:
                superior_note = note_generator.generate_superior_note(group, topic)
                all_superior_notes.append(superior_note)
            except Exception as e:
                print(f"Error generando nota para el grupo {i+1}: {e}")
                continue

        print(f"✅ Proceso completado. Se generaron {len(all_superior_notes)} Notas Superiores.")
        final_results = {'status': 'success', 'topic': topic, 'superior_notes': all_superior_notes, 'total_groups_found': len(grouped_news), 'notes_generated': len(all_superior_notes)}
        _save_search_results(search_key, final_results)

    except Exception as e:
        print(f"❌ Error crítico en el proceso de búsqueda: {e}")
        error_results = {'status': 'error', 'message': f'Error procesando la búsqueda: {str(e)}', 'topic': topic}
        _save_search_results(search_key, error_results)
    finally:
        if search_key in active_searches:
            del active_searches[search_key]
            print(f"La búsqueda '{search_key}' ha sido marcada como finalizada.")
