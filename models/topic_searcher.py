import os
import json
import re
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_ollama.llms import OllamaLLM

class TopicSearcher:
    """
    Clase que utiliza IA para buscar noticias por tema, identificar eventos clave y recopilar
    múltiples fuentes con su contenido completo, sin depender de selectores HTML.
    """

    def __init__(self):
        """Inicializa el buscador con herramientas de IA."""
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = OllamaLLM(model="llama3", base_url=ollama_base_url, temperature=0.0)
        self.search_tool = TavilySearchResults(max_results=20)
        self.reliable_domains = [
            "elpais.com", "elmundo.es", "abc.es", "lavanguardia.com", # España
            "clarin.com", "lanacion.com.ar", "infobae.com", "pagina12.com.ar", # Argentina
            "xataka.com", "genbeta.com", "wired.com", "theverge.com", "techcrunch.com", # Tecnología
            "bbc.com/mundo" # Internacional
        ]
        print("🤖 TopicSearcher (versión IA) inicializado.")

    def search_topic_news(self, topic, hours_back=24, max_sources=5):
        """
        Orquesta el flujo de búsqueda de noticias dirigido por IA.
        """
        print(f"▶️  Paso 1: Identificando eventos clave para '{topic}'...")
        key_event_queries = self._get_key_events(topic, hours_back)

        if not key_event_queries:
            print(f"🟡 No se identificaron eventos clave para '{topic}'.")
            return []

        print(f"✅ Eventos clave identificados: {key_event_queries}")
        all_event_groups = []
        for event_query in key_event_queries:
            print(f"\n▶️  Paso 2 y 3: Buscando fuentes y extrayendo contenido para '{event_query}'...")
            articles_group = self._get_sources_for_event(event_query, max_sources)

            if articles_group and len(articles_group) >= 2:
                print(f"✅ Grupo de artículos encontrado para '{event_query}' con {len(articles_group)} fuentes.")
                all_event_groups.append(articles_group)
            else:
                print(f"🟡 No se encontraron suficientes fuentes para el evento '{event_query}'.")

        return all_event_groups

    def _get_key_events(self, topic, hours_back):
        """
        Usa la IA para buscar noticias generales y luego identificar los eventos más importantes.
        """
        try:
            search_query = f"últimas noticias sobre {topic}"
            initial_results = self.search_tool.invoke({"query": search_query, "search_depth": "advanced"})

            if not initial_results:
                return []

            headlines = "\n".join([f"- {res['title']}" for res in initial_results])

            prompt = f"""
            A partir de la siguiente lista de titulares de noticias recientes sobre "{topic}", tu tarea es actuar como un editor jefe.
            Identifica los 3 a 5 eventos o historias noticiosas más importantes y distintas.
            Para cada evento, genera un término de búsqueda en español, muy específico y neutral que usarías para encontrar más artículos sobre esa historia exacta.

            Reglas:
            - No inventes eventos que no estén en la lista.
            - Devuelve el resultado únicamente en formato JSON, como una lista de strings.
            - Ejemplo de respuesta: {{"eventos": ["anuncio del nuevo chip de Intel", "debate sobre la ley de IA en el parlamento europeo", "compra de una startup de IA por parte de Apple"]}}

            Titulares:
            {headlines}
            """

            response = self.llm.invoke(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                print(f"Error: La IA no devolvió un JSON válido para los eventos clave. Respuesta: {response}")
                return []

            parsed_json = json.loads(json_match.group(0))
            return parsed_json.get("eventos", [])
        except Exception as e:
            print(f"❌ Error en _get_key_events: {e}")
            return []

    def _get_sources_for_event(self, event_query, max_sources):
        """
        Para un evento específico, busca en dominios confiables y extrae el contenido completo.
        """
        try:
            sites_query_part = " OR ".join([f"site:{domain}" for domain in self.reliable_domains])
            full_query = f'"({event_query})" ({sites_query_part})' # Corrected f-string
            results = self.search_tool.invoke({"query": full_query, "search_depth": "advanced", "include_raw_content": True})

            articles = []
            if not results:
                return []

            for res in results[:max_sources]:
                if res.get("raw_content"):
                    source_name = "Fuente Desconocida"
                    match = re.search(r'https://(?:www\.)?([^/]+)', res['url'])
                    if match:
                        source_name = match.group(1)

                    articles.append({
                        'title': res['title'],
                        'url': res['url'],
                        'summary': res['content'],
                        'source': source_name.split('.')[0].capitalize(),
                        'content': res['raw_content']
                    })
            return articles
        except Exception as e:
            print(f"❌ Error en _get_sources_for_event: {e}")
            return []
