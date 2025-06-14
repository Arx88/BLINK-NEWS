import os
import json
import re
import random
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_ollama.llms import OllamaLLM

class TopicSearcher:
    """
    Clase que utiliza IA para encontrar artículos relevantes y luego busca
    fuentes similares basadas en keywords para garantizar la robustez.
    """

    def __init__(self):
        """Inicializa el buscador con herramientas de IA y dominios categorizados."""
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = OllamaLLM(model="llama3", base_url=ollama_base_url, temperature=0.0)
        self.search_tool = TavilySearchResults(max_results=10)
        self.source_finder_tool = TavilySearchResults(max_results=3)

        self.domain_categories = {
            "argentina": [
                "clarin.com", "lanacion.com.ar", "infobae.com", "pagina12.com.ar", "perfil.com",
                "cronista.com", "ambito.com", "tn.com.ar", "diariopopular.com.ar", "lacapital.com.ar",
                "lavoz.com.ar", "losandes.com.ar", "lagaceta.com.ar", "eldia.com", "cronica.com.ar",
                "minutouno.com", "iprofesional.com", "telam.com.ar", "agenciapacourondo.com.ar"
            ],
            "spain": [
                "elpais.com", "elmundo.es", "abc.es", "lavanguardia.com", "elconfidencial.com",
                "elespanol.com", "larazon.es", "publico.es", "eldiario.es", "20minutos.es",
                "lainformacion.com", "huffingtonpost.es"
            ],
            "sports": [
                "marca.com", "as.com", "sport.es", "mundodeportivo.com", "ole.com.ar", "tycsports.com",
                "espn.com", "espn.com.ar", "foxsports.com", "bleacherreport.com", "theathletic.com",
                "lequipe.fr", "gazzetta.it", "libero.pe", "depor.com"
            ],
            "technology": [
                "xataka.com", "genbeta.com", "hipertextual.com", "techcrunch.com", "theverge.com",
                "wired.com", "cnet.com", "gizmodo.com", "engadget.com", "arstechnica.com",
                "digitaltrends.com", "techradar.com", "thenextweb.com", "venturebeat.com",
                "mashable.com", "fayerwayer.com"
            ],
            "blockchain_crypto": [
                "coindesk.com", "cointelegraph.com", "theblockcrypto.com", "decrypt.co",
                "beincrypto.com", "beincrypto.es", "criptonoticias.com", "diariobitcoin.com",
                "crypto.news", "u.today"
            ],
            "economy_finance": [
                "wsj.com", "bloomberg.com", "ft.com", "forbes.com", "economist.com",
                "expansion.com", "cincodias.elpais.com", "portafolio.co", "df.cl",
                "elfinanciero.com.mx", "eleconomista.com.mx"
            ],
            "international": [
                "reuters.com", "apnews.com", "bbc.com/mundo", "cnn.com", "cnnespanol.cnn.com",
                "theguardian.com", "nytimes.com", "washingtonpost.com", "aljazeera.com",
                "dw.com", "france24.com", "euronews.com", "efe.com", "afp.com"
            ]
        }
        print("🤖 TopicSearcher (v14.0 - Lógica Final Simplificada) inicializado.")

    def search_topic_news(self, topic, hours_back=24, max_sources=5):
        print(f"▶️  Paso 1: Buscando artículos base para '{topic}' de las últimas {hours_back} horas...")
        initial_articles = self._fetch_initial_articles(topic, hours_back)

        if not initial_articles:
            print(f"🟡 No se encontraron artículos iniciales para '{topic}'.")
            return []
        
        print(f"✅ Encontrados {len(initial_articles)} artículos base. Procesando los más relevantes...")
        
        all_event_groups = []
        # Iteramos sobre los artículos base encontrados para intentar formar grupos
        for base_article in initial_articles:
            # Si ya tenemos suficientes notas superiores, paramos.
            if len(all_event_groups) >= 2: # Limitamos a 2 notas superiores por búsqueda
                 break

            print(f"\n▶️  Paso 2: Intentando formar un grupo a partir del artículo: \"{base_article.get('title')}\"")
            similar_articles = self._find_similar_articles(base_article, max_sources)
            
            # El grupo de artículos lo conforma el artículo base + los similares encontrados
            articles_group = [base_article] + similar_articles
            
            if len(articles_group) >= 2:
                print(f"✅ Grupo de artículos encontrado con {len(articles_group)} fuentes.")
                all_event_groups.append(articles_group)
            else:
                print(f"🟡 No se encontraron suficientes fuentes similares para este artículo.")

        if not all_event_groups:
             print(f"🔴 No se pudo formar ningún grupo de noticias con múltiples fuentes para '{topic}'.")

        return all_event_groups

    def _fetch_initial_articles(self, topic, hours_back):
        try:
            search_query = f"noticias de {topic}"
            recency_in_days = (hours_back + 23) // 24
            
            print(f"  -> Búsqueda inicial con filtro de tiempo: {recency_in_days} día(s).")
            
            search_results = self.search_tool.invoke({
                "query": search_query,
                "recency_days": recency_in_days,
                "include_raw_content": True # Pedimos el contenido desde el inicio
            })
            
            if not search_results or not isinstance(search_results, list): 
                print("🟡 La búsqueda inicial no devolvió resultados.")
                return []
            
            # Filtramos para asegurarnos de que los artículos tengan contenido
            return [res for res in search_results if isinstance(res, dict) and res.get('raw_content')]
        except Exception as e:
            print(f"❌ Error en _fetch_initial_articles: {e}")
            return []

    def _find_similar_articles(self, base_article, max_sources):
        try:
            title = base_article.get('title', '')
            content_snippet = base_article.get('content', '')
            
            # Tarea simple y directa para la IA
            prompt_keywords = f"Extrae las 5 palabras o entidades clave más importantes del siguiente título y resumen. Devuelve solo las palabras separadas por comas, sin explicaciones. Título: {title}. Resumen: {content_snippet[:300]}"
            keywords_str = self.llm.invoke(prompt_keywords)
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]

            if not keywords: 
                print("   -> La IA no pudo extraer keywords.")
                return []
            
            search_query = " ".join(keywords)
            print(f"  -> Buscando artículos similares con keywords: '{search_query}'")
            
            all_domains = list(set(sum(self.domain_categories.values(), [])))
            original_url = base_article.get('url', '')
            
            # Excluimos el dominio del artículo original para no encontrarlo a él mismo
            original_domain_match = re.search(r'https://(?:www\.)?([^/]+)', original_url)
            original_domain = original_domain_match.group(1) if original_domain_match else ''
            
            domains_to_search = [d for d in all_domains if d != original_domain]
            shuffled_domains = random.sample(domains_to_search, len(domains_to_search))
            
            found_articles = []
            for domain in shuffled_domains:
                if len(found_articles) >= max_sources - 1: break
                
                query = f'"{search_query}" site:{domain}'
                
                try:
                    results = self.source_finder_tool.invoke({"query": query, "include_raw_content": True})
                    if not results or not isinstance(results, list): continue

                    for res in results:
                        if len(found_articles) >= max_sources - 1: break
                        if isinstance(res, dict) and res.get("raw_content"):
                            if res.get('url') == original_url: continue
                            if any(a['url'] == res.get('url') for a in found_articles): continue
                            
                            print(f"    [+] Encontrado similar: {res.get('url')}")
                            source_name = domain.split('.')[0].capitalize()
                            
                            found_articles.append({
                                'title': res.get('title', search_query), 'url': res.get('url'),
                                'summary': res.get('content'), 'source': source_name,
                                'content': res.get('raw_content')
                            })
                            break
                except Exception:
                    continue
            return found_articles
        except Exception as e:
            print(f"❌ Error en _find_similar_articles: {e}")
            return []