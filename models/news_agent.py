# models/news_agent.py

from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from models.agent_tools import buscar_en_la_web, leer_contenido_web

def crear_agente_de_noticias():
    """
    Crea y configura el agente de IA con sus herramientas y lógica.
    """
    # 1. Inicializar el modelo de Ollama
    llm = OllamaLLM(model="llama3") # Asegúrate de que 'llama3' esté disponible en Ollama

    # 2. Definir la lista de herramientas que el agente puede usar
    tools = [buscar_en_la_web, leer_contenido_web]

    # 3. Crear el prompt (las instrucciones para el cerebro del agente)
    # Este prompt le dice al agente cómo debe comportarse y usar sus herramientas.
    prompt_template = """
    Eres un periodista de IA experto. Tu objetivo es investigar un tema a fondo y escribir una nota periodística completa y objetiva.

    Tienes acceso a las siguientes herramientas:
    {tools}

    Para cumplir tu objetivo, sigue estos pasos:
    1.  Usa la herramienta 'buscar_en_la_web' para encontrar varias fuentes de noticias confiables sobre el tema.
    2.  Analiza los resultados de la búsqueda y selecciona 2 o 3 de las URLs más relevantes.
    3.  Para cada URL seleccionada, usa la herramienta 'leer_contenido_web' para extraer el texto completo.
    4.  Una vez que tengas el contenido de todas las fuentes, sintetiza la información, contrasta los puntos de vista y genera tu respuesta final.

    Tu respuesta final debe ser la nota periodística completa, bien estructurada y redactada profesionalmente.
    No describas los pasos que tomaste, solo presenta el resultado final.

    Comienza la investigación para el siguiente tema:
    Tema: {input}

    Historial de conversación y pensamiento:
    {agent_scratchpad}
    """
    prompt = PromptTemplate.from_template(prompt_template)

    # 4. Crear el agente que une el LLM, las herramientas y el prompt
    agent = create_react_agent(llm, tools, prompt)

    # 5. Crear el ejecutor del agente, que es el que realmente corre el ciclo de pensamiento y acción
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    return agent_executor
