# Guardar como: news-blink-backend/src/routes/topic_search.py

from flask import Blueprint, jsonify, request
import os
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_ollama.llms import OllamaLLM
import hashlib
from datetime import datetime

# Toda la lógica está ahora en una única ruta para máxima simplicidad
topic_search_bp = Blueprint('topic_search', __name__)

@topic_search_bp.route('/search-topic', methods=['POST'])
def search_topic_sync():
    """
    Esta es una ruta síncrona y de bloqueo.
    Recibe un tema, busca en Tavily, genera una nota con Ollama y la devuelve.
    """
    data = request.get_json()
    if not data or 'topic' not in data or not data['topic'].strip():
        return jsonify({'error': 'Se requiere un tema válido'}), 400
    
    topic = data['topic']
    print(f"✅ [SYNC] Recibida búsqueda para el tema: '{topic}'")

    try:
        # 1. INICIALIZAR HERRAMIENTAS
        print("-> Inicializando herramientas (Tavily, Ollama)...")
        tavily_search = TavilySearchResults(max_results=5)
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        llm = OllamaLLM(model="qwen3:32b", base_url=ollama_base_url, temperature=0.3)

        # 2. BUSCAR NOTICIAS
        print(f"-> Buscando en Tavily sobre '{topic}'...")
        search_results = tavily_search.invoke(f"noticias de {topic} en las últimas 24 horas")
        
        # 3. CREAR PROMPT PARA EL LLM
        print("-> Creando prompt para el LLM...")
        context = "## Contexto de Noticias Recientes:\n\n"
        if isinstance(search_results, list) and search_results:
            for result in search_results:
                context += f"- Fuente: {result.get('url')}\n  Contenido: {result.get('content')}\n\n"
        else:
            context += "No se encontraron resultados de noticias recientes."

        prompt_para_llm = f"""
Eres un periodista experto. Basándote EXCLUSIVAMENTE en el siguiente contexto sobre "{topic}", redacta una nota periodística completa y objetiva.

Instrucciones:
- Crea un título principal para la nota.
- Estructura el contenido con subtítulos claros.
- Sintetiza la información de las fuentes en un texto fluido y coherente.
- No inventes datos. No menciones que eres una IA. Escribe directamente el artículo.

{context}

Ahora, por favor, escribe la nota periodística completa:
        """
        
        # 4. GENERAR NOTA
        print("-> Invocando a Ollama para generar la nota...")
        nota_generada = llm.invoke(prompt_para_llm)

        # 5. DEVOLVER RESULTADO
        note_id = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest()
        superior_note = {
            'id': note_id,
            'topic': topic,
            'title': f"Análisis sobre: {topic}",
            'full_content': nota_generada,
            'ultra_summary': [], # Esto se puede implementar después
            'sources': [res.get('url') for res in search_results] if isinstance(search_results, list) else [],
            'urls': [res.get('url') for res in search_results] if isinstance(search_results, list) else [],
            'articles_count': len(search_results) if isinstance(search_results, list) else 0,
            'timestamp': datetime.now().isoformat(),
            'image': None,
        }
        
        final_result = {
            'status': 'completed',
            'results': {
                'topic': topic,
                'superior_notes': [superior_note]
            }
        }
        
        print("✅ [SYNC] Búsqueda completada. Devolviendo resultado.")
        # Esta ruta ahora devuelve el resultado completo directamente
        return jsonify(final_result)

    except Exception as e:
        print(f"❌ [SYNC] Error durante la búsqueda: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Ha ocurrido un error interno: {str(e)}'}), 500