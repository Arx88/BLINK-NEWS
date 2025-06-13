# models/news_agent.py

from langchain_ollama.llms import OllamaLLM
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from models.agent_tools import buscar_en_la_web, leer_contenido_web

def crear_agente_de_noticias():
    """
    Crea y configura el agente de IA con sus herramientas y lógica.
    """
    # 1. Inicializar el modelo de Ollama
    llm = OllamaLLM(model="llama3")

    # 2. Definir la lista de herramientas
    tools = [buscar_en_la_web, leer_contenido_web]

    # 3. Cargar un prompt probado y compatible desde LangChain Hub
    # Este prompt está específicamente diseñado para agentes ReAct y ya
    # tiene la estructura correcta de 'Thought/Action/Observation'.
    # Nos ahorra tener que adivinar el formato exacto.
    prompt = hub.pull("hwchase17/react")

    # 4. Crear el agente que une el LLM, las herramientas y el prompt
    # La función se asegura de que el prompt reciba las variables correctas.
    agent = create_react_agent(llm, tools, prompt)

    # 5. Crear el ejecutor del agente
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor