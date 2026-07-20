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
