# 🛡️ Agentes de IA para Blue Teams

Curso prático de 10 dias para times de segurança aprenderem a construir e integrar agentes de IA no dia a dia do blue team.

## 📚 Estrutura do Curso

| Dia | Tema | Duração |
|-----|------|---------|
| [Dia 1](./dia-01-setup-e-primeira-integracao.md) | Setup do ambiente + primeira integração com Agno + conceitos de IA | ~1h30 |
| [Dia 2](./dia-02-chat-roles-temperatura.md) | Modo chat, system/user/assistant, temperatura, thinking, search | ~1h |
| [Dia 3](./dia-03-prompt-engineering.md) | Prompt Engineering, formato de saída, arquivos (txt, pdf, imagem) | ~1h |
| [Dia 4](./dia-04-ia-generativa-vs-agentes-agno.md) | IA Generativa vs Agentes + Agno core (tools, memória, sessões) | ~1h |
| [Dia 5](./dia-05-agno-avancado-agentui.md) | Agno avançado (reasoning, teams, knowledge, workflows) | ~1h |
| [Dia 6](./dia-06-interfaces-agentui-gradio.md) | Interfaces: AgentOS, AgentUI e Gradio | ~1h |
| [Dia 7](./dia-07-openrouter.md) | OpenRouter — um endpoint, todos os modelos | ~1h |
| [Dia 8](./dia-08-mcp-fastmcp-context7.md) | MCP, FastMCP e Context7 | ~1h |
| [Dia 9](./dia-09-fastapi.md) | Servindo agentes com FastAPI — do zero ao endpoint em produção | ~1h |
| [Dia 10](./dia-10-skills-superpowers-metodologia.md) | Skills, Superpowers, Graphify, SDD e Harness Engineering | ~1h |

## 🛠️ Pré-requisitos

- Conhecimento básico de programação (Python de preferência)
- Conta na [OpenAI Platform](https://platform.openai.com) (API key)
- Conta no [OpenRouter](https://openrouter.ai) (Dia 7)
- Conta na [Anthropic Console](https://console.anthropic.com) (Dias 4+)
- Node.js instalado (Dia 6 — AgentUI)

## ⚡ Quickstart

```bash
# 1. Clonar o repositório
git clone <url-do-repo>
cd agente-seguranca

# 2. Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Instalar dependências
uv sync

# 4. Configurar credenciais
cp .env.example .env
# Edite o .env com suas API keys

# 5. Rodar o primeiro exemplo
uv run python main.py
```

## 🔐 Segurança

- **Nunca commite o arquivo `.env`** — ele está no `.gitignore`
- Use `.env.example` como template para outros desenvolvedores
- Rotacione suas API keys periodicamente
- Monitore o uso na dashboard do provedor para detectar vazamentos
