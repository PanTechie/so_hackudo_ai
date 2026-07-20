# NVIDIA DeepSeek V4 Flash Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configurar o agente SOC para gerar respostas com `deepseek-ai/deepseek-v4-flash` pela integração nativa da NVIDIA no Agno.

**Architecture:** O modelo de chat será trocado de `OpenAIChat` para `Nvidia`, preservando a base LanceDB e o `OpenAIEmbedder`. Um teste estático validará a configuração sem importar o script, evitando ingestão de documentos e chamadas externas durante os testes.

**Tech Stack:** Python 3.13, Agno 2.6+, pytest, LanceDB, OpenAI embeddings, NVIDIA API.

## Global Constraints

- Usar o ID exato `deepseek-ai/deepseek-v4-flash`.
- Usar `temperature=1`, `top_p=0.95` e `extra_body={"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}}`.
- Manter `OpenAIEmbedder(id="text-embedding-3-small")` e a configuração existente da LanceDB.
- Não alterar prompts, documentos ou a pergunta de exemplo.
- Não modificar `.env.example`, pois ele já contém alterações locais fora deste trabalho.

---

### Task 1: Configurar o modelo NVIDIA no agente SOC

**Files:**
- Create: `tests/test_agente_com_knowledge.py`
- Modify: `agente_com_knowledge.py:1-35`

**Interfaces:**
- Consumes: `agno.models.nvidia.Nvidia` e as variáveis de ambiente `NVIDIA_API_KEY` e `OPENAI_API_KEY` lidas pelas integrações do Agno.
- Produces: variável global `agente: Agent` configurada com `Nvidia(id="deepseek-ai/deepseek-v4-flash", ...)`.

- [ ] **Step 1: Escrever o teste que falha**

```python
import ast
from pathlib import Path


SOURCE_PATH = Path(__file__).parents[1] / "agente_com_knowledge.py"


def _calls_by_name(tree: ast.AST, name: str) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    ]


def test_uses_nvidia_deepseek_and_keeps_openai_embeddings():
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))

    imports = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert ("agno.models.nvidia", "Nvidia") in imports
    assert ("agno.models.openai", "OpenAIChat") not in imports

    nvidia_call, = _calls_by_name(tree, "Nvidia")
    nvidia_config = {
        keyword.arg: ast.literal_eval(keyword.value)
        for keyword in nvidia_call.keywords
    }
    assert nvidia_config == {
        "id": "deepseek-ai/deepseek-v4-flash",
        "temperature": 1,
        "top_p": 0.95,
        "extra_body": {
            "chat_template_kwargs": {
                "thinking": True,
                "reasoning_effort": "high",
            }
        },
    }

    embedder_call, = _calls_by_name(tree, "OpenAIEmbedder")
    embedder_config = {
        keyword.arg: ast.literal_eval(keyword.value)
        for keyword in embedder_call.keywords
    }
    assert embedder_config == {"id": "text-embedding-3-small"}
```

- [ ] **Step 2: Executar o teste e confirmar a falha esperada**

Run: `uv run --with pytest pytest tests/test_agente_com_knowledge.py -v`

Expected: FAIL porque `agno.models.nvidia.Nvidia` ainda não é importado e o agente ainda usa `OpenAIChat`.

- [ ] **Step 3: Implementar a configuração mínima**

Substituir o import do modelo:

```python
from agno.models.nvidia import Nvidia
```

Substituir a configuração `model` do agente:

```python
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
```

- [ ] **Step 4: Executar o teste e confirmar sucesso**

Run: `uv run --with pytest pytest tests/test_agente_com_knowledge.py -v`

Expected: `1 passed`.

- [ ] **Step 5: Verificar sintaxe, estilo e diff**

Run: `uv run python -m py_compile agente_com_knowledge.py tests/test_agente_com_knowledge.py`

Expected: exit code 0 e nenhuma saída.

Run: `uv run ruff check agente_com_knowledge.py tests/test_agente_com_knowledge.py`

Expected: `All checks passed!`.

Run: `git diff --check -- agente_com_knowledge.py tests/test_agente_com_knowledge.py`

Expected: exit code 0 e nenhuma saída.

- [ ] **Step 6: Commitar a implementação**

```bash
git add agente_com_knowledge.py tests/test_agente_com_knowledge.py
git commit -m "feat: use NVIDIA DeepSeek for SOC agent"
```
