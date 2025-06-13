# models/agent_tools.py

from langchain.tools import tool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import time

@tool
def buscar_en_la_web(query: str) -> str:
    """
    Realiza una búsqueda en Google y devuelve los 5 mejores resultados.
    Usa esta herramienta para encontrar URLs de noticias relevantes sobre un tema.
    """
    print(f"🤖 Usando herramienta de BÚSQUEDA-SELENIUM para: '{query}'")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")

        # Encuentra la barra de búsqueda, escribe la consulta y presiona Enter
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(2) # Esperar a que la página de resultados cargue

        # Extraer los resultados
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = []
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title_elem = g.find('h3')
                title = title_elem.text if title_elem else "Sin título"

                # Evitar enlaces internos de Google
                if link.startswith("http"):
                    results.append({"title": title, "href": link})
                    if len(results) >= 5: # Limitar a 5 resultados
                        break

        if not results:
            return "No se encontraron resultados."

        return "
".join([
            f"Título: {res['title']}
URL: {res['href']}
---"
            for res in results
        ])

    except Exception as e:
        return f"Error durante la búsqueda web con Selenium: {e}"
    finally:
        if driver:
            driver.quit()


@tool
def leer_contenido_web(url: str) -> str:
    """
    Lee y extrae el contenido textual limpio de una página web a partir de su URL.
    Usa esta herramienta DESPUÉS de haber encontrado una URL con 'buscar_en_la_web'.
    """
    print(f"🤖 Usando herramienta de LECTURA-SELENIUM para: '{url}'")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
            element.decompose()

        body_text = soup.body.get_text(separator=' ', strip=True)
        cleaned_text = re.sub(r'\s+', ' ', body_text)

        return cleaned_text[:8000]
    except Exception as e:
        return f"Error al leer la URL {url}: {e}"
    finally:
        if driver:
            driver.quit()
```
