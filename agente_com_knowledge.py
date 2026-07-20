from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.nvidia import Nvidia
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.embedder.openai import OpenAIEmbedder

load_dotenv()

# ── Criando a base de conhecimento ───────────────────────────────────
knowledge_base = Knowledge(
    vector_db=LanceDb(
        table_name="soc_knowledge",
        uri="tmp/lancedb",
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

# Carrega os documentos na primeira execução
# (nas próximas, já está no banco — comente esta linha)
knowledge_base.insert(
    name="SOC Documents",
    path="knowledge/",
    skip_if_exists=True,
)

# ── Agente que usa a knowledge base ──────────────────────────────────
agente = Agent(
    name="SOC Assistant",
    model=Nvidia(
        id="deepseek-ai/deepseek-v4-flash",
        temperature=1,
        top_p=0.95,
        extra_body={
            "chat_template_kwargs": {
                "thinking": True,
                "reasoning_effort": "high",
            }
        },
    ),
    knowledge=knowledge_base,
    description="""Assistente do SOC com acesso aos playbooks e políticas da empresa.
    Sempre consulte a base de conhecimento antes de responder.""",
    instructions=[
        "Consulte sempre os playbooks internos quando disponíveis",
        "Cite o documento fonte quando usar informações da knowledge base",
        "Se não encontrar na knowledge base, indique que está usando conhecimento geral",
    ],
    search_knowledge=True,  # Permite ao agente buscar na knowledge base
    markdown=True,
)

agente.print_response(
    "Nosso playbook de ransomware diz para isolar o sistema imediatamente? "
    "Qual o procedimento completo?",
    stream=True,
)
