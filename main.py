import os
import json
import httpx
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from dotenv import load_dotenv

load_dotenv()


@tool
def verificar_ip_abuseipdb(ip: str) -> str:
    """
    Consulta o AbuseIPDB para verificar se um IP foi reportado como abusivo.
    Retorna score de abuso, total de reports e país de origem.
    """
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        return "ABUSEIPDB_API_KEY não configurada no .env"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                "https://api.abuseipdb.com/api/v2/check",
                headers={"Key": api_key, "Accept": "application/json"},
                params={"ipAddress": ip, "maxAgeInDays": 90},
            )
            response.raise_for_status()
            dados = response.json()["data"]

        return (
            f"IP: {ip}\n"
            f"País: {dados.get('countryCode', 'Desconhecido')}\n"
            f"Score de abuso: {dados['abuseConfidenceScore']}%\n"
            f"Total de reports: {dados['totalReports']}\n"
            f"ISP: {dados.get('isp', 'N/A')}\n"
            f"Último report: {dados.get('lastReportedAt', 'Nunca')}"
        )
    except httpx.RequestError as e:
        return f"Erro de conexão: {e}"


agente = Agent(
    model=OpenAIChat(id="gpt-5.4"),
    tools=[verificar_ip_abuseipdb],
    description="Analista de IR com habilidade de verificar informações de IP",
    markdown=True,
)

agente.print_response("Verifique o Ip 8.8.8.8")
