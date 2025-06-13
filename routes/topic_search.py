from flask import Blueprint, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
import time

from models.topic_searcher import TopicSearcher
from models.superior_note_generator import SuperiorNoteGenerator
from models.news_agent import crear_agente_de_noticias # <-- NUEVO IMPORT
import hashlib # Ensure hashlib is imported

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
    """Procesa la búsqueda por tema en segundo plano USANDO EL AGENTE DE IA"""
    try:
        print(f"🤖 Agente de IA iniciando investigación para el tema: {topic}")
        
        # Actualizar estado
        # Ensure active_searches is defined and accessible here
        # For example, it might be a global variable in this file
        # active_searches = {} # If it's not defined elsewhere
        active_searches[search_key]['status'] = 'generating_notes' # El agente hace todo en un paso
        
        # 1. Crear el agente
        agent_executor = crear_agente_de_noticias()

        # 2. Invocar al agente para que realice su trabajo
        # Esto puede tardar varios minutos
        prompt_para_agente = f"Investiga a fondo y redacta una nota periodística completa sobre '{topic}', basándote en noticias de las últimas {hours_back} horas."
        resultado_agente = agent_executor.invoke({"input": prompt_para_agente})
        
        nota_generada = resultado_agente.get('output', 'No se pudo generar la nota.')

        # 3. Formatear la salida del agente en la estructura esperada
        # (Esta parte se puede mejorar para que el agente devuelva un JSON estructurado)
        superior_note = {
            'id': hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest(),
            'topic': topic,
            'title': f"Análisis Autónomo sobre: {topic}", # Título simple
            'full_content': nota_generada,
            'ultra_summary': [ # Resumen simple por ahora
                "Análisis generado por un agente de IA autónomo.",
                "Múltiples fuentes web fueron consultadas en tiempo real.",
                "La información fue extraída y sintetizada automáticamente."
            ],
            'sources': ["Web Autónoma"],
            'urls': [], # El agente no nos devuelve las URLs directamente en este flujo simple
            'articles_count': "Varias",
            'timestamp': datetime.now().isoformat(),
            'image': None,
        }
        
        results = {
            'status': 'success',
            'topic': topic,
            'superior_notes': [superior_note], # Envolvemos en una lista
            'total_groups_found': 1,
            'notes_generated': 1,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Ensure _save_search_results is defined and accessible
        # def _save_search_results(key, data): pass # Example if not defined
        _save_search_results(search_key, results)
        
        print(f"✅ Investigación del agente completada para el tema: {topic}")
        
    except Exception as e:
        print(f"❌ Error en el proceso del agente de IA: {e}")
        _save_search_results(search_key, {
            'status': 'error',
            'message': f'Error en el agente de IA: {str(e)}',
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        })
    finally:
        # La limpieza de active_searches se maneja como antes
        pass

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

