from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

load_dotenv()

agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    description="Analista de segurança blue team.",
    markdown=True,
)

agente.print_response("Liste os 5 IoCs mais comuns em ataques de phishing.")
