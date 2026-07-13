from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team, TeamMode
from agno.tools.websearch import WebSearchTools
from dotenv import load_dotenv

load_dotenv()


# ── Agente 1: Especialista em Network ────────────────────────────
analista_network = Agent(
    name="Network Analyst",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Especialista em análise de tráfego de rede e IOCs de IP/domínio.",
    instructions=[
        "Analise IPs, domínios e padrões de tráfego",
        "Identifique técnicas MITRE ATT&CK relacionadas à rede",
        "Foque em: lateral movement, C2, exfiltração",
    ],
    tools=[WebSearchTools()],
    markdown=True,
)

# ── Agente 2: Especialista em Endpoint ───────────────────────────
analista_endpoint = Agent(
    name="Endpoint Analyst",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Especialista em análise de endpoints, processos e artefatos de malware.",
    instructions=[
        "Analise processos, arquivos, registry e persistence mechanisms",
        "Identifique técnicas MITRE ATT&CK relacionadas ao endpoint",
        "Foque em: execution, persistence, privilege escalation",
    ],
    markdown=True,
)

# ── Agente 3: Especialista em Threat Intelligence ─────────────────
analista_ti = Agent(
    name="Threat Intel Analyst",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Especialista em Threat Intelligence e atribuição de ataques.",
    instructions=[
        "Correlacione IOCs com grupos de ameaça conhecidos",
        "Identifique TTPs e padrões de ataque",
        "Pesquise em fontes públicas de inteligência",
    ],
    tools=[WebSearchTools()],
    markdown=True,
)

# ── Líder: Incident Commander ──────────────────────────────────────
incident_commander = Team(
    name="SOC Incident Response Team",
    mode=TeamMode.coordinate,  # Coordena todos em paralelo e consolida
    model=OpenAIChat(id="gpt-4o"),  # Modelo mais capaz para o líder
    members=[analista_network, analista_endpoint, analista_ti],
    description="Time de resposta a incidentes que coordena múltiplos especialistas.",
    instructions=[
        "Distribua a investigação entre os especialistas conforme suas áreas",
        "Consolide as análises em um relatório unificado",
        "Priorize ações de contenção imediata",
        "Produza um relatório final estruturado com: Sumário Executivo, "
        "Timeline, Análise Técnica, Atribuição e Plano de Remediação",
    ],
    markdown=True,
)

# Incidente a ser investigado
incident_commander.print_response(
    "Temos um incidente em andamento. "
    "IP 185.220.101.45 (Tor exit node) fez login SSH como root no prod-01. "
    "Detectamos execução de script malicioso, criação de backdoor e "
    "movimentação lateral para o banco de dados. "
    "Investiguem em paralelo e me deem um relatório completo.",
    stream=True,
)
