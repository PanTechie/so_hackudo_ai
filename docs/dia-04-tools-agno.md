# 🛡️ Agentes de IA para Blue Teams — Dia 4: Tools do Agno

> **Duração estimada:** ~1 hora  
> **Pré-requisito:** Dias 1 a 3 concluídos  
> **Objetivo:** Explorar as tools prontas do Agno e criar tools personalizadas para segurança

---

## 📋 O que vamos fazer hoje

1. Tools prontas do Agno úteis para segurança
2. Tools personalizadas com `httpx`
3. Agente de Threat Intelligence completo
4. Memória persistente entre sessões

---

## 1. Tools Prontas do Agno

Nos dias anteriores já usamos `WebSearchTools`. O Agno tem dezenas de tools prontas. As mais relevantes para segurança:

### WebSearchTools — Busca na Web

Já usamos no Dia 2. Recapitulando o padrão para compor com outras tools:

```python
from agno.tools.websearch import WebSearchTools
...
    tools=[WebSearchTools()]
...
```

### PythonTools — Executa Código Python

O agente pode escrever e executar código Python para análise:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.python import PythonTools

agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    tools=[PythonTools()],
    description="Analista forense que pode executar scripts Python.",
    markdown=True,
)

agente.print_response(
    "Escreva e execute um script que verifique quais desses IPs "
    "pertencem a ranges de Tor exit nodes conhecidos: "
    "185.220.101.45, 192.168.1.10, 8.8.8.8, 51.15.43.205"
)
```

### FileTools — Lê e Escreve Arquivos

```python
from agno.tools.file import FileTools

agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    tools=[FileTools(base_dir="logs/")],
    description="Analista de logs com acesso ao sistema de arquivos.",
    markdown=True,
)

agente.print_response(
    "Leia o auth.log e identifique tentativas de brute force nas últimas 24h."
)
```

### ShellTools — Executa Comandos do Sistema

> ⚠️ Use com cuidado — ideal para ambientes controlados.

```python
from agno.tools.shell import ShellTools

agente = Agent(
    model=OpenAIChat(id="gpt-5.4"),
    tools=[ShellTools()],
    description="Agente de resposta a incidentes com acesso ao shell.",
    markdown=True,
)

agente.print_response(
    "Liste as conexões de rede ativas e identifique "
    "processos com conexões para portas incomuns."
)
```

### Combinando tools

Um agente pode ter múltiplas tools — ele decide qual usar em cada momento:

```python
agente = Agent(
    model=OpenAIChat(id="gpt-5.4"),
    tools=[
        WebSearchTools(),
        FileTools(base_dir="logs/"),
        ShellTools(),
    ],
    description="Analista de IR com acesso a web, arquivos e shell.",
    markdown=True,
)
```

---

## 2. Tools Personalizadas com httpx

Quando as tools prontas não cobrem o que você precisa, criamos as nossas. Basta uma função Python com type hints e docstring — o Agno gera o schema automaticamente.

`httpx` é a biblioteca HTTP moderna do Python — substituta do `requests` com suporte nativo a async e HTTP/2.

```bash
uv add httpx
```

### Tool: Verificar IP no AbuseIPDB

```python
# tools/threat_intel.py
import httpx
import os
from agno.tools import tool

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
```

### Tool: Verificar Hash no MalwareBazaar

```python
@tool
def verificar_hash_malwarebazaar(hash_value: str) -> str:
    """
    Consulta o MalwareBazaar para verificar se um hash é malware conhecido.
    Aceita MD5, SHA1 ou SHA256.
    """
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                "https://mb-api.abuse.ch/api/v1/",
                data={"query": "get_info", "hash": hash_value},
            )
            resultado = response.json()

        if resultado["query_status"] == "hash_not_found":
            return f"Hash não encontrado no MalwareBazaar. (Não garante benignidade)"

        info = resultado["data"][0]
        return (
            f"⚠️  MALWARE CONFIRMADO\n"
            f"Nome: {info.get('file_name', 'N/A')}\n"
            f"Família: {info.get('signature', 'N/A')}\n"
            f"Tipo: {info.get('file_type', 'N/A')}\n"
            f"Tags: {', '.join(info.get('tags') or ['Nenhuma'])}\n"
            f"Primeira submissão: {info.get('first_seen', 'N/A')}"
        )
    except httpx.RequestError as e:
        return f"Erro de conexão: {e}"
```

### Por que `@tool` e não só uma função?

O decorator `@tool` instrui o Agno a:
1. Gerar o schema JSON da função (nome, parâmetros, tipos, descrição)
2. Registrar a função como tool disponível para o modelo
3. Executar a função quando o modelo decidir chamá-la
4. Devolver o resultado ao modelo para continuar o raciocínio

Sem o decorator, é só uma função Python comum — o modelo não sabe que ela existe.

---

## 3. Agente de Threat Intelligence Completo

```python
# agente_threat_intel.py
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.websearch import WebSearchTools
from tools.threat_intel import verificar_ip_abuseipdb, verificar_hash_malwarebazaar

load_dotenv()

agente_ti = Agent(
    name="Threat Intelligence Analyst",
    model=OpenAIChat(id="gpt-5.4"),
    description="""Analista de Threat Intelligence especializado.
    Use as ferramentas para investigar IOCs e ameaças.
    Sempre correlacione múltiplas fontes antes de concluir.""",
    instructions=[
        "Para IPs suspeitos: verifique AbuseIPDB E pesquise na web",
        "Para hashes: sempre verifique o MalwareBazaar",
        "Classifique: CONFIRMADA | SUSPEITA | FALSO POSITIVO",
        "Inclua recomendações de contenção específicas",
    ],
    tools=[
        verificar_ip_abuseipdb,
        verificar_hash_malwarebazaar,
        WebSearchTools(),
    ],
    markdown=True,
)

agente_ti.print_response(
    "Investigue o IP 185.220.101.45 que fez login SSH no nosso servidor. "
    "É malicioso? O que devo fazer?",
    stream=True,
)
```

---

## 4. Memória Persistente entre Sessões

Nos dias anteriores o chat mantinha memória durante a execução com `num_history_sessions`. Mas ao reiniciar o script, perdia tudo. Com `SqliteStorage` a memória persiste entre execuções:

```python
# chat_persistente.py
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

load_dotenv()

agente = Agent(
    name="Blue Team Assistant",
    model=OpenAIChat(id="gpt-5.4-mini"),
    description="Analista de segurança blue team.",
    db=SqliteStorage(
        table_name="blue_team_chat",
        db_file="tmp/agente.db",
    ),
    num_history_sessions=10,
    markdown=True,
)

# session_id fixo = mesma memória entre execuções
agente.cli_app(session_id="sessao-principal", markdown=True)
```

```bash
# Execução 1
uv run python chat_persistente.py
> Você: Meu nome é Carlos, sou analista L2 no SOC.
> Agente: Olá Carlos!

# Ctrl+C — encerra

# Execução 2 — processo novo, memória preservada
uv run python chat_persistente.py
> Você: Qual é o meu nome?
> Agente: Seu nome é Carlos, você é analista L2 no SOC.
```

### Múltiplas sessões (um agente, vários analistas)

```python
# multi_sessao.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

storage = SqliteStorage(table_name="sessoes_soc", db_file="tmp/sessoes.db")

def criar_sessao(analista_id: str) -> Agent:
    return Agent(
        model=OpenAIChat(id="gpt-5.4-mini"),
        description="Analista de segurança blue team.",
        storage=storage,
        num_history_sessions=5,
        markdown=True,
    )

# Cada analista tem seu próprio histórico isolado
agente = criar_sessao("carlos")
agente.print_response(
    "Investigando movimentação lateral no prod-01.",
    session_id="carlos-20250615"
)
```

---

## ✅ Checklist do Dia 4

- [ ] Testou PythonTools, FileTools e ShellTools
- [ ] Criou tools personalizadas com `@tool` e `httpx`
- [ ] Agente de Threat Intelligence completo funcionando
- [ ] Memória persistente com SQLite funcionando entre execuções

---

## 📚 Referências

- [Agno — Tools disponíveis](https://docs.agno.com/tools/overview)
- [Agno — Custom Tools](https://docs.agno.com/tools/custom-tools)
- [httpx — Documentação](https://www.python-httpx.org/)
- [AbuseIPDB API](https://www.abuseipdb.com/api)
- [MalwareBazaar API](https://bazaar.abuse.ch/api/)

---

> **Próxima aula (Dia 5):** Agno avançado — reasoning, teams de agentes especializados, knowledge base com RAG e workflows determinísticos.
