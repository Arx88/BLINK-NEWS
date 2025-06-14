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

        # Dominios confiables para la búsqueda de noticias.
        # LISTA FINAL Y EXPANDIDA con más de 300 fuentes, basada en tu feedback.
        self.reliable_domains = [
            # === ARGENTINA (Ampliación) ===
            "clarin.com", "lanacion.com.ar", "infobae.com", "pagina12.com.ar", "perfil.com",
            "cronista.com", "ambito.com", "ole.com.ar", "tn.com.ar", "diariopopular.com.ar",
            "lacapital.com.ar", "lavoz.com.ar", "losandes.com.ar", "lagaceta.com.ar",
            "eldia.com", "cronica.com.ar", "minutouno.com", "iprofesional.com", "telam.com.ar",
            "agenciapacourondo.com.ar", "diariojornada.com.ar", "elancasti.com.ar", "elchubut.com.ar",
            "eldiariodelarepublica.com", "ellitoral.com", "primeraedicion.com.ar", "laarena.com.ar",

            # === ESPAÑA ===
            "elpais.com", "elmundo.es", "abc.es", "lavanguardia.com", "elconfidencial.com",
            "elespanol.com", "larazon.es", "publico.es", "eldiario.es", "okdiario.com",
            "libertaddigital.com", "vozpopuli.com", "cincodias.elpais.com", "expansion.com",
            "elperiodico.com", "20minutos.es", "lainformacion.com", "huffingtonpost.es",
            "heraldo.es", "lavozdegalicia.es", "elcorreo.com", "farodevigo.es", "diariovasco.com",
            "diariodenavarra.es", "ideal.es", "lasprovincias.es", "diariosur.es", "ultimahora.es",

            # === DEPORTES (Ampliación) ===
            "marca.com", "as.com", "sport.es", "mundodeportivo.com", "superdeporte.es",
            "estadiodeportivo.com", "tycsports.com", "espn.com", "espn.com.ar", "espn.com.mx",
            "foxsports.com", "bleacherreport.com", "cbssports.com", "nbcsports.com",
            "skysports.com", "deadspin.com", "theathletic.com", "lequipe.fr", "gazzetta.it",
            "futbolred.com", "libero.pe", "depor.com",

            # === TECNOLOGÍA (Ampliación) ===
            "xataka.com", "genbeta.com", "hipertextual.com", "techcrunch.com", "theverge.com",
            "wired.com", "cnet.com", "gizmodo.com", "engadget.com", "arstechnica.com",
            "digitaltrends.com", "techradar.com", "thenextweb.com", "venturebeat.com",
            "mashable.com", "fayerwayer.com", "microsiervos.com", "neowin.net", "techspot.com",
            "howtogeek.com", "anandtech.com", "tomshardware.com", "polygon.com", "kotaku.com",

            # === BLOCKCHAIN / CRIPTOMONEDAS ===
            "coindesk.com", "cointelegraph.com", "theblockcrypto.com", "decrypt.co",
            "beincrypto.com", "beincrypto.es", "criptonoticias.com", "diariobitcoin.com",
            "crypto.news", "bitcoin.com/news", "news.bitcoin.com", "u.today",

            # === MÉXICO ===
            "eluniversal.com.mx", "reforma.com", "milenio.com", "jornada.com.mx", "elfinanciero.com.mx",
            "eleconomista.com.mx", "excelsior.com.mx", "proceso.com.mx", "aristeguinoticias.com",
            "sinembargo.mx", "sopitas.com", "unotv.com", "sdpnoticias.com",

            # === COLOMBIA ===
            "eltiempo.com", "elespectador.com", "semana.com", "larepublica.co", "portafolio.co",
            "elcolombiano.com", "elpais.com.co", "vanguardia.com", "elheraldo.co", "lasillavacia.com",
            "pulzo.com",

            # === CHILE, PERÚ, VENEZUELA, ECUADOR, URUGUAY, BOLIVIA, PARAGUAY, COSTA RICA ===
            "emol.com", "latercera.com", "cooperativa.cl", "biobiochile.cl", "df.cl",
            "elmostrador.cl", "eldinamo.cl", "lun.com", "elcomercio.pe", "gestion.pe",
            "larepublica.pe", "rpp.pe", "diariocorreo.pe", "peru21.pe", "expreso.com.pe",
            "eluniversal.com", "elnacional.com", "ultimasnoticias.com.ve", "talcualdigital.com",
            "el-carabobeno.com", "elcomercio.com", "eluniverso.com", "expreso.ec",
            "lahora.com.ec", "elpais.com.uy", "elobservador.com.uy", "montevideo.com.uy",
            "republica.com.uy", "eldeber.com.bo", "la-razon.com", "paginasiete.bo",
            "lostiempos.com", "abc.com.py", "ultimahora.com", "lanacion.com.py",
            "nacion.com", "teletica.com", "crhoy.com",

            # === USA (Principales en Inglés y Español) ===
            "nytimes.com", "washingtonpost.com", "wsj.com", "apnews.com", "reuters.com",
            "cnn.com", "nbcnews.com", "cbsnews.com", "abcnews.go.com", "usatoday.com",
            "bloomberg.com", "forbes.com", "theguardian.com/us", "latimes.com", "chicagotribune.com",
            "bostonglobe.com", "npr.org", "pbs.org/newshour", "time.com", "theatlantic.com",
            "newyorker.com", "politico.com", "thehill.com", "axios.com", "propublica.org",
            "univision.com/noticias", "telemundo.com",

            # === REINO UNIDO ===
            "bbc.com/news", "theguardian.com", "reuters.co.uk", "independent.co.uk", "ft.com",
            "thetimes.co.uk", "telegraph.co.uk", "dailymail.co.uk", "mirror.co.uk",
            "standard.co.uk", "metro.co.uk", "thesun.co.uk", "spectator.co.uk",

            # === INTERNACIONAL Y AGENCIAS ===
            "ap.org", "afp.com", "efe.com", "dpa.com", "xinhuanet.com",
            "tass.com", "aljazeera.com", "dw.com", "france24.com", "euronews.com",
            "foreignpolicy.com", "economist.com", "foreignaffairs.com",

            # === OTROS MEDIOS GLOBALES RELEVANTES ===
            "lemonde.fr", "lefigaro.fr", # Francia
            "spiegel.de", "faz.net", "sueddeutsche.de", # Alemania
            "corriere.it", "repubblica.it", # Italia
            "folha.uol.com.br", "oglobo.globo.com", # Brasil
            "theglobeandmail.com", "cbc.ca/news", # Canadá
            "asahi.com", "japantimes.co.jp", # Japón
            "thehindu.com", "timesofindia.indiatimes.com", # India
            "smh.com.au", "theage.com.au", # Australia
        ]
        print("🤖 TopicSearcher (versión IA) inicializado con lista de dominios expandida y categorizada.")

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
            
            # --- PASO DE DEPURACIÓN ---
            print("\n--- DEBUG: RESPUESTA CRUDA DE TAVILY ---")
            print(initial_results)
            print("--- FIN DEL DEBUG ---\n")
            # --- FIN DEL PASO DE DEPURACIÓN ---

            if not initial_results:
                return []

            # Verificamos que la clave 'title' exista en cada resultado antes de usarla.
            headlines = "\n".join([f"- {res.get('title')}" for res in initial_results if 'title' in res and res.get('title')])

            if not headlines:
                print("🟡 No se encontraron titulares válidos en los resultados de búsqueda inicial.")
                return []
            
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
            # Imprimimos el error completo para tener más detalles
            import traceback
            print(f"❌ Error en _get_key_events: {e}")
            traceback.print_exc()
            return []

    def _get_sources_for_event(self, event_query, max_sources):
        """
        Para un evento específico, busca en dominios confiables y extrae el contenido completo.
        """
        try:
            sites_query_part = " OR ".join([f"site:{domain}" for domain in self.reliable_domains])
            full_query = f'"{event_query}" ({sites_query_part})'
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