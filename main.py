from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.websearch import WebSearchTools
from dotenv import load_dotenv

load_dotenv()

agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    description="Analista de threat intelligence com acesso à internet.",
    instructions=[
        "Sempre busque informações atualizadas antes de responder",
        "Cite as fontes encontradas",
        "Foque em fontes confiáveis: NIST, MITRE, CVE.org, Bleeping Computer",
    ],
    tools=[WebSearchTools()],  # ← adiciona capacidade de busca
    markdown=True,
)

agente.print_response(
    "Quais CVEs críticas (CVSS >= 9.0) foram divulgadas nos últimos 60 dias "
    "que afetam servidores Linux? Liste CVE ID, descrição e sistemas afetados.",
    stream=True,
)
