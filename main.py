import json
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools

from dotenv import load_dotenv

load_dotenv()

agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    tools=[FileTools(base_dir=Path("logs/"))],
    description="Analista de logs com acesso ao sistema de arquivos.",
    markdown=True,
)

agente.print_response(
    "Leia o auth.log e identifique tentativas de brute force nas últimas 24h."
)
