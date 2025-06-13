# models/news_agent.py
import os
from langchain_ollama.llms import OllamaLLM
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults

def crear_agente_de_noticias():
    """Crea y configura el agente de IA con el prompt correcto."""

    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = OllamaLLM(model="qwen3:32b", base_url=ollama_base_url)

    tools = [TavilySearchResults(max_results=5)]

    # --- LÍNEA CORREGIDA ---
    # Cambiamos el prompt a "hwchase17/react", que está diseñado para
    # agentes de tipo "ReAct" y no requiere historial de chat.
    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        # Devolver los pasos intermedios para poder ver el razonamiento si es necesario
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent_executor
