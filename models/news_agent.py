import os
from langchain_ollama.llms import OllamaLLM
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults

def crear_agente_de_noticias():
    """Crea y configura el agente de IA con la herramienta Tavily Search."""

    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = OllamaLLM(model="qwen3:32b", base_url=ollama_base_url)

    # La única herramienta que necesitamos ahora es Tavily
    # max_results=5 le dice que se enfoque en los 5 resultados más importantes
    tools = [TavilySearchResults(max_results=5)]

    # Usamos el prompt de LangChain para agentes conversacionales con herramientas
    prompt = hub.pull("hwchase17/react-chat")

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent_executor
