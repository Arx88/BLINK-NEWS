from flask import Blueprint, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
import time

from models.topic_searcher import TopicSearcher
from models.superior_note_generator import SuperiorNoteGenerator

# Crear blueprint para las rutas de búsqueda por tema
topic_search_bp = Blueprint('topic_search', __name__)

# Inicializar modelos
topic_searcher = TopicSearcher()
superior_note_generator = SuperiorNoteGenerator()

# Variable global para tracking de búsquedas en progreso
active_searches = {}

@topic_search_bp.route('/search-topic', methods=['POST'])
def search_topic():
    """API para buscar noticias por tema específico"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'error': 'Se requiere especificar un tema'
            }), 400
        
        topic = data['topic'].strip()
        hours_back = data.get('hours_back', 24)
        max_sources = data.get('max_sources', 5)
        
        if not topic:
            return jsonify({
                'error': 'El tema no puede estar vacío'
            }), 400
        
        # Verificar si ya hay una búsqueda en progreso para este tema
        search_key = f"{topic.lower()}_{hours_back}"
        if search_key in active_searches:
            return jsonify({
                'status': 'processing',
                'message': f'Búsqueda en progreso para "{topic}". Por favor espere...',
                'topic': topic
            })
        
        # Marcar búsqueda como activa
        active_searches[search_key] = {
            'topic': topic,
            'started_at': datetime.now().isoformat(),
            'status': 'searching'
        }
        
        # Iniciar búsqueda en segundo plano
        threading.Thread(
            target=process_topic_search,
            args=(topic, hours_back, max_sources, search_key),
            daemon=True
        ).start()
        
        return jsonify({
            'status': 'started',
            'message': f'Iniciando búsqueda para "{topic}". Esto puede tomar unos minutos...',
            'topic': topic,
            'search_key': search_key
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error procesando solicitud: {str(e)}'
        }), 500

@topic_search_bp.route('/search-status/<search_key>', methods=['GET'])
def get_search_status(search_key):
    """API para obtener el estado de una búsqueda"""
    try:
        if search_key not in active_searches:
            return jsonify({
                'status': 'not_found',
                'message': 'Búsqueda no encontrada'
            }), 404
        
        search_info = active_searches[search_key]
        
        # Verificar si hay resultados disponibles
        results = _get_search_results(search_key)
        if results:
            # Limpiar búsqueda activa
            del active_searches[search_key]
            return jsonify({
                'status': 'completed',
                'results': results
            })
        
        return jsonify({
            'status': search_info['status'],
            'topic': search_info['topic'],
            'started_at': search_info['started_at']
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error obteniendo estado: {str(e)}'
        }), 500

@topic_search_bp.route('/superior-notes', methods=['GET'])
def get_superior_notes():
    """API para obtener todas las notas superiores"""
    try:
        notes = superior_note_generator.get_all_superior_notes()
        
        return jsonify({
            'status': 'success',
            'notes': notes,
            'count': len(notes)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error obteniendo notas superiores: {str(e)}'
        }), 500

@topic_search_bp.route('/superior-note/<note_id>', methods=['GET'])
def get_superior_note(note_id):
    """API para obtener una nota superior específica"""
    try:
        notes = superior_note_generator.get_all_superior_notes()
        note = next((n for n in notes if n['id'] == note_id), None)
        
        if not note:
            return jsonify({
                'error': 'Nota no encontrada'
            }), 404
        
        return jsonify({
            'status': 'success',
            'note': note
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error obteniendo nota: {str(e)}'
        }), 500

def process_topic_search(topic, hours_back, max_sources, search_key):
    """Procesa la búsqueda por tema en segundo plano"""
    try:
        print(f"Iniciando búsqueda para tema: {topic}")
        
        # Actualizar estado
        active_searches[search_key]['status'] = 'searching_news'
        
        # Buscar noticias por tema
        news_groups = topic_searcher.search_topic_news(
            topic=topic,
            hours_back=hours_back,
            max_sources=max_sources
        )
        
        if not news_groups:
            # No se encontraron noticias
            _save_search_results(search_key, {
                'status': 'no_results',
                'message': f'No se encontraron noticias sobre "{topic}" en las últimas {hours_back} horas',
                'topic': topic,
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # Actualizar estado
        active_searches[search_key]['status'] = 'generating_notes'
        
        # Generar notas superiores para cada grupo
        superior_notes = []
        
        for i, news_group in enumerate(news_groups[:3]):  # Limitar a 3 grupos principales
            try:
                print(f"Generando nota superior {i+1}/{min(len(news_groups), 3)}")
                
                superior_note = superior_note_generator.generate_superior_note(
                    articles_group=news_group,
                    topic=topic
                )
                
                superior_notes.append(superior_note)
                
            except Exception as e:
                print(f"Error generando nota superior para grupo {i+1}: {e}")
                continue
        
        # Guardar resultados
        results = {
            'status': 'success',
            'topic': topic,
            'superior_notes': superior_notes,
            'total_groups_found': len(news_groups),
            'notes_generated': len(superior_notes),
            'timestamp': datetime.now().isoformat(),
            'search_params': {
                'hours_back': hours_back,
                'max_sources': max_sources
            }
        }
        
        _save_search_results(search_key, results)
        
        print(f"Búsqueda completada para tema: {topic}. Generadas {len(superior_notes)} notas superiores")
        
    except Exception as e:
        print(f"Error en búsqueda por tema: {e}")
        
        # Guardar error
        _save_search_results(search_key, {
            'status': 'error',
            'message': f'Error procesando búsqueda: {str(e)}',
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        })
    
    finally:
        # Limpiar de búsquedas activas después de un tiempo
        def cleanup_search():
            time.sleep(300)  # 5 minutos
            if search_key in active_searches:
                del active_searches[search_key]
        
        threading.Thread(target=cleanup_search, daemon=True).start()

def _save_search_results(search_key, results):
    """Guarda los resultados de una búsqueda"""
    try:
        # Crear directorio si no existe
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'topic_searches')
        os.makedirs(results_dir, exist_ok=True)
        
        # Guardar resultados
        filename = f"search_{search_key}.json"
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Resultados de búsqueda guardados: {filepath}")
        
    except Exception as e:
        print(f"Error guardando resultados de búsqueda: {e}")

def _get_search_results(search_key):
    """Obtiene los resultados de una búsqueda"""
    try:
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'topic_searches')
        filename = f"search_{search_key}.json"
        filepath = os.path.join(results_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
        
    except Exception as e:
        print(f"Error obteniendo resultados de búsqueda: {e}")
        return None

