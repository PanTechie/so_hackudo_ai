import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.websearch import WebSearchTools
from agno.media import Image

from dotenv import load_dotenv

load_dotenv()

agente_triagem = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    description="""Sistema automatizado de triagem de alertas de segurança.
    Analise cada alerta e retorne APENAS JSON válido com esta estrutura:
    {
      "severidade": "CRÍTICO | ALTO | MÉDIO | BAIXO",
      "tipo": "tipo do ataque",
      "falso_positivo_provavel": true/false,
      "confianca": 0-100,
      "resumo": "uma frase",
      "acoes_imediatas": ["ação 1", "ação 2"]
    }""",
)


def triar_alerta(alerta: str) -> dict:
    resposta = agente_triagem.run(f"Alerta: {alerta}", stream=False)
    return json.loads(resposta.content)


alertas = [
    "Failed password for root from 185.220.101.45 port 4892 ssh2 - 47 attempts in 60s",
    "User admin logged in from 192.168.1.100 at 09:30 (regular working hours)",
    "Process 'mimikatz.exe' detected on WORKSTATION-42 by EDR",
    "Port scan detected from 10.0.0.50 to 10.0.0.0/24 (internal scanner - Nessus)",
]

print("🛡️  Triagem Automatizada de Alertas\n")
for i, alerta in enumerate(alertas, 1):
    resultado = triar_alerta(alerta)
    emoji = {"CRÍTICO": "🔴", "ALTO": "🟠", "MÉDIO": "🟡", "BAIXO": "🟢"}.get(
        resultado["severidade"], "⚪"
    )
    print(f"Alerta {i}: {emoji} {resultado['severidade']} | {resultado['tipo']}")
    print(f"  Resumo: {resultado['resumo']}")
    print(
        f"  Falso positivo: {resultado['falso_positivo_provavel']} "
        f"(confiança: {resultado['confianca']}%)"
    )
    print()
