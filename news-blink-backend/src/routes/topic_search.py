# Guardar como: news-blink-backend/src/routes/topic_search.py

from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime
import threading
import time
import hashlib

# Importamos las herramientas que SÍ funcionan
from models.topic_searcher import TopicSearcher
from models.superior_note_generator import SuperiorNoteGenerator

topic_search_bp = Blueprint('topic_search', __name__)

# Dependencias que usará nuestro orquestador
topic_searcher = TopicSearcher()
superior_note_generator = SuperiorNoteGenerator()

# Diccionario para seguir el estado de las búsquedas asíncronas
active_searches = {}

# --- Funciones de Ayuda para manejar archivos de resultados ---

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


# --- Rutas de la API ---

@topic_search_bp.route('/search-topic', methods=['POST'])
def search_topic():
    """API para iniciar una búsqueda por tema. Responde rápido y deja el trabajo pesado en un hilo."""
    data = request.get_json()
    if not data or 'topic' not in data or not data['topic'].strip():
        return jsonify({'error': 'Se requiere especificar un tema'}), 400

    topic = data['topic'].strip()
    hours_back = data.get('hours_back', 24)
    max_sources = data.get('max_sources', 5)
    search_key = f"{topic.lower().replace(' ', '_')}_{hours_back}"

    if search_key in active_searches:
        return jsonify({
            'status': 'processing',
            'message': f'Búsqueda ya en progreso para "{topic}". Por favor espere...',
            'topic': topic
        })

    # Limpia resultados anteriores y marca la nueva búsqueda como iniciada
    _delete_search_results(search_key)
    active_searches[search_key] = {
        'topic': topic,
        'started_at': datetime.now().isoformat(),
        'status': 'starting'
    }

    # Inicia el proceso pesado en un hilo separado para no bloquear la API
    threading.Thread(
        target=orchestrate_topic_search,
        args=(topic, hours_back, max_sources, search_key),
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
    """API que el frontend consulta para ver el progreso y obtener el resultado final."""
    if search_key in active_searches:
        # La búsqueda aún está en progreso
        return jsonify(active_searches[search_key])

    # Si ya no está en búsquedas activas, puede que haya terminado
    results = _get_search_results(search_key)
    if results:
        return jsonify({'status': 'completed', 'results': results})
    
    # Si no está activa y no hay resultados, no se encontró
    return jsonify({'status': 'not_found', 'message': 'Búsqueda no encontrada o expirada.'}), 404


# --- El Orquestador ---

def orchestrate_topic_search(topic, hours_back, max_sources, search_key):
    """
    Esta función es el "director de orquesta". Se ejecuta en segundo plano
    y sigue los pasos que definimos para crear una Nota Superior.
    """
    try:
        print(f"✅ ORQUESTADOR: Iniciando para el tema: '{topic}'")
        
        # Paso 1 y 2: Búsqueda Exploratoria y Cruzada
        active_searches[search_key]['status'] = 'searching_news'
        print(f"-> ORQUESTADOR: Usando TopicSearcher para encontrar grupos de noticias...")
        news_groups = topic_searcher.search_topic_news(
            topic=topic, hours_back=hours_back, max_sources=max_sources
        )
        
        if not news_groups:
            print(f"-> ORQUESTADOR: No se encontraron grupos de noticias para '{topic}'.")
            _save_search_results(search_key, {'status': 'no_results', 'message': 'No se encontraron noticias relevantes.'})
            return

        # Paso 3 y 4: Síntesis Imparcial y Resumen Ejecutivo
        active_searches[search_key]['status'] = 'generating_notes'
        print(f"-> ORQUESTADOR: Se encontraron {len(news_groups)} grupos. Procesando los más importantes...")
        
        superior_notes = []
        # Limitamos a procesar un máximo de 2 notas superiores para no tardar demasiado
        for i, group in enumerate(news_groups[:2]):
            try:
                print(f"--> ORQUESTADOR: Grupo {i+1}, generando Nota Superior con {len(group)} fuentes.")
                # Aquí usamos la herramienta que ya tenías para esto
                note = superior_note_generator.generate_superior_note(articles_group=group, topic=topic)
                superior_notes.append(note)
            except Exception as e:
                print(f"--> ORQUESTADOR: Error generando nota para un grupo: {e}")
                continue

        if not superior_notes:
            print(f"-> ORQUESTADOR: No se pudo generar ninguna Nota Superior.")
            _save_search_results(search_key, {'status': 'no_results', 'message': 'La IA no pudo procesar las noticias encontradas.'})
            return

        # Paso 5: Presentación
        final_results = {
            'status': 'success',
            'topic': topic,
            'superior_notes': superior_notes,
            'total_groups_found': len(news_groups),
            'notes_generated': len(superior_notes),
            'timestamp': datetime.now().isoformat()
        }
        
        _save_search_results(search_key, final_results)
        print(f"✅ ORQUESTADOR: Proceso completado exitosamente para '{topic}'.")

    except Exception as e:
        print(f"❌ ORQUESTADOR: Error fatal en el proceso de búsqueda: {e}")
        import traceback
        traceback.print_exc()
        _save_search_results(search_key, {'status': 'error', 'message': str(e)})
    finally:
        # Limpiamos la búsqueda de la lista de activas para que la próxima consulta obtenga el archivo
        if search_key in active_searches:
            del active_searches[search_key]