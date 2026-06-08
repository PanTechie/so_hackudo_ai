# 🛡️ Agentes de IA para Blue Teams — Dia 1: Setup + Primeira Integração

> **Duração estimada:** ~1 hora  
> **Público:** Time de segurança com conhecimento básico de programação  
> **Objetivo:** Configurar o ambiente do zero e fazer a primeira chamada à IA com Agno

---

## 📋 O que vamos fazer hoje

1. Instalar o VSCode com extensões essenciais
2. Entender TOML e Markdown
3. Instalar o UV e inicializar o projeto
4. Boas práticas de segurança no código (`.env`, `.gitignore`, `git`)
5. Instalar dependências e fazer a primeira chamada com Agno
6. Entender o que é IA Generativa e os modelos disponíveis

---

## 1. Editor de Código: VSCode

Um editor de código não é apenas um bloco de notas. Ele oferece syntax highlighting, autocomplete inteligente, integração com ferramentas e terminal integrado — tudo em um só lugar.

Usaremos o **VSCode** ao longo de todo o curso. É gratuito, tem o ecossistema de extensões mais rico do mercado e é o editor mais adotado na indústria.

**Download:** https://code.visualstudio.com/

### Alternativas para explorar depois

- **Cursor** (https://cursor.sh) — VSCode com IA integrada nativamente. Autocompletar e chat de código muito mais poderosos que o GitHub Copilot. Vale muito testar quando quiser ir além.
- **Antigravity** (https://antigravity.google) — IDE agent-first do Google, lançado em novembro de 2025. Fork do VS Code focado em agentes autônomos: você delega tarefas para agentes que planejam, escrevem e testam código em paralelo. Powered by Gemini 3, gratuito durante o preview público.

---

## 2. Extensões Essenciais do VSCode

Abra o VSCode, vá em **Extensions** (`Ctrl+Shift+X`) e instale cada uma:

### 🔴 Error Lens
Exibe erros e avisos diretamente na linha do código — sem precisar passar o mouse. Em vez de um sublinhado vermelho misterioso, você vê a mensagem de erro ao lado do código.

**Instalar:** buscar `Error Lens` (autor: usernamehw)

### 🐍 Ruff
Linter e formatador de Python ultra-rápido, escrito em Rust. Substitui `flake8`, `isort` e `black` em uma única ferramenta. Avisa sobre código ruim, formata e organiza imports automaticamente.

**Instalar:** buscar `Ruff` (autor: Astral Software)

### 🔍 Ty
Type checker para Python, também da Astral. Python é dinamicamente tipado, mas com type hints o `ty` verifica inconsistências antes de executar o código — essencial para código de produção.

```python
# Exemplo de type hint que o ty verifica:
def analisar_log(caminho: str) -> list[str]:
    ...
```

**Instalar:** buscar `Ty` (autor: Astral Software)

> ⚠️ O `ty` é relativamente novo. Se não encontrar, o `Pylance` é uma alternativa consolidada.

### 🤖 Claude Code for VS Code
Extensão oficial da Anthropic que integra o Claude diretamente no VSCode — para explicar código, sugerir correções, gerar testes e muito mais sem sair do editor.

**Instalar:** buscar `Claude Code` (autor: Anthropic)

### 📄 Even Better TOML
Suporte avançado para arquivos `.toml` — syntax highlighting, validação, autocomplete. Sem essa extensão, o `pyproject.toml` aparece como texto plano.

**Instalar:** buscar `Even Better TOML` (autor: tamasfe)

---

## 3. Formatos de Arquivo: TOML e Markdown

### 📝 Markdown (.md)

Linguagem de marcação leve para formatar texto com símbolos simples como `#`, `*`, `-`.

**Por que usamos:** documentação de projetos (`README.md`), este arquivo do curso, GitHub renderiza automaticamente.

```markdown
# Título grande
## Subtítulo

**negrito**, *itálico*, `código`

- item de lista
- outro item
```

**No VSCode:** `Ctrl+Shift+V` para visualizar renderizado.

### ⚙️ TOML

Formato de configuração legível por humanos, sem ambiguidade. O UV usa TOML para configurar o projeto (`pyproject.toml`). Mais legível que JSON e aceita comentários com `#`.

```toml
[project]
name = "agente-seguranca"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.ruff]
line-length = 88
```

---

## 4. UV — Gerenciador de Projetos Python Moderno

UV é uma ferramenta da **Astral** (mesma equipe do Ruff) que substitui `pip`, `venv`, `poetry` e `pyenv` em um único comando. É escrito em Rust — extremamente rápido — e está se tornando o padrão da indústria.

### Instalando o UV

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
uv --version  # verificar instalação
```

### Inicializando o projeto

```bash
uv init agente-seguranca
cd agente-seguranca
```

**O que o UV cria:**

```
agente-seguranca/
├── .python-version   ← versão do Python (garante consistência entre máquinas)
├── .venv/            ← ambiente virtual isolado
├── pyproject.toml    ← configuração do projeto
├── README.md
└── hello.py          ← arquivo de exemplo (vamos renomear para main.py)
```

> 💡 **Por que o `.venv/` importa em segurança:** cada projeto tem dependências isoladas. Uma vulnerabilidade em um pacote de um projeto não afeta os outros.

### Instalando Ruff e Ty como ferramentas de dev

```bash
uv add --dev ruff ty
```

O `--dev` significa que são ferramentas de desenvolvimento — ficam separadas das dependências que o código de produção precisa. O `pyproject.toml` atualiza automaticamente:

```toml
[dependency-groups]
dev = [
    "ruff>=0.8.0",
    "ty>=0.0.1a6",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
```

```bash
uv run ruff check .    # verificar problemas
uv run ruff format .   # formatar código
```

---

## 5. Boas Práticas de Segurança no Código

Antes da primeira linha de código que usa uma API, precisamos falar sobre segurança.

### ⚠️ O problema das credenciais no código

```python
# ❌ ERRADO — chave hardcoded no código
agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini", api_key="sk-proj-abc123..."),
)
```

Se commitar no Git, a chave fica exposta para sempre no histórico. Bots escaneiam repositórios públicos em busca de chaves em segundos — já houve casos de faturas de **milhares de dólares** por esse motivo.

### Criando o `.env`

```bash
touch .env
```

```env
# Chaves de API — NUNCA commitar este arquivo!
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

### Criando o `.gitignore`

```bash
touch .gitignore
```

```gitignore
# Variáveis de ambiente — NUNCA versionar!
.env
.env.local
.env.*.local

# Ambiente virtual
.venv/
__pycache__/
*.pyc

# Sistema e IDEs
.DS_Store
.vscode/settings.json

# Outputs
*.log
tmp/
```

> 💡 Crie o `.gitignore` **antes** do primeiro commit. Adicionar depois pode não ser suficiente se o arquivo já foi trackeado.

### Criando o `.env.example`

Template sem valores reais — este sim vai para o Git:

```bash
touch .env.example
```

```env
# Copie para .env e preencha com suas credenciais
OPENAI_API_KEY=sua-chave-aqui
```

### Inicializando o Git

```bash
git status        # UV pode ter iniciado o git automaticamente
git init          # se não inicializou
git add .
git commit -m "feat: setup inicial do projeto"
```

> 🔍 `git status` não deve mostrar o `.env`. Se mostrar, revise o `.gitignore`.

---

## 6. Instalando as Dependências

```bash
# python-dotenv: carrega o .env automaticamente
# agno: framework de agentes (já inclui o SDK da OpenAI internamente)
# openai: SDK da OpenAI
uv add python-dotenv agno openai
```

---

## 7. Primeira Chamada com Agno — "Olá, IA!"

Renomeie `hello.py` para `main.py` e escreva:

```python
# main.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    description="Analista de segurança blue team.",
    markdown=True,
)

agente.print_response(
    "Liste os 5 IoCs mais comuns em ataques de phishing."
)
```

```bash
uv run python main.py
```

### Explicando o código

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
```
`Agent` é o núcleo do Agno. `OpenAIChat` é o wrapper para os modelos da OpenAI.

```python
agente = Agent(
    model=OpenAIChat(id="gpt-5.4-mini"),
    description="...",
    markdown=True,
)
```
Cria o agente. `OpenAIChat` lê a `OPENAI_API_KEY` automaticamente do ambiente. `description` define o comportamento — é o que o modelo recebe como instrução de sistema. `markdown=True` formata a saída no terminal.

```python
agente.print_response("...")
```
Envia a mensagem, recebe a resposta e imprime formatada. O Agno cuida de toda a comunicação HTTP, tratamento de erros e formatação por baixo dos panos.

---

## 8. O que é IA Generativa?

IA Generativa é uma categoria de IA capaz de **criar conteúdo novo** — texto, código, imagens — aprendendo padrões de grandes volumes de dados.

```
Dados de treinamento (internet, livros, código)
        ↓
   Modelo aprende padrões de linguagem
        ↓
   Você envia um prompt
        ↓
   Modelo prediz os tokens mais prováveis
        ↓
   Resposta gerada
```

**Conceito chave:** o modelo não "sabe" a resposta — ele prediz a sequência de palavras mais provável dado o contexto.

**Por que importa para segurança:**
- Pode ser **manipulado** via inputs maliciosos (prompt injection)
- Pode **alucinar** — gerar informações falsas com confiança
- Pode escalar ataques (phishing em massa gerado por IA)
- E também **defender** — triagem de alertas, análise de logs, correlação de eventos

---

## 9. Modelos de Linguagem — Diferenças e Quando Usar

Um modelo é o resultado do treinamento — bilhões de parâmetros que definem como ele processa e gera texto. A OpenAI lança versões novas a cada 6–8 semanas, então sempre vale checar https://platform.openai.com/docs/models.

### Família OpenAI (maio 2026)

| Modelo | Velocidade | Custo (input / output por 1M tokens) | Quando usar |
|--------|-----------|--------------------------------------|-------------|
| `gpt-5.4-mini` | ⚡⚡⚡ | $0,75 / $4,50 | Alto volume, triagem rápida, protótipos |
| `gpt-5.4` | ⚡⚡ | $2,50 / $15,00 | Análise complexa, produção, padrão atual |
| `gpt-5.5` | ⚡⚡ | $5,00 / $30,00 | Máxima capacidade de raciocínio e código |
| `gpt-5.4-pro` | ⚡ | $30,00 / $180,00 | Decisões críticas, análise forense profunda |

```
Alto volume / resposta rápida  → gpt-5.4-mini
Análise complexa em produção   → gpt-5.4
Máxima capacidade / código     → gpt-5.5
Decisão crítica / forense      → gpt-5.4-pro
```

### Trocar de modelo no Agno é uma linha

```python
# Triagem rápida — barato e rápido
agente = Agent(model=OpenAIChat(id="gpt-5.4-mini"), ...)

# Análise forense — mais capaz
agente = Agent(model=OpenAIChat(id="gpt-5.4"), ...)
```

Toda a lógica do agente permanece igual. Só o `id` muda.

---

## 10. Estrutura Final do Projeto

```
agente-seguranca/
├── .env              ← credenciais (NÃO vai pro Git)
├── .env.example      ← template (vai pro Git)
├── .gitignore
├── .git/
├── .python-version
├── .venv/
├── pyproject.toml
├── README.md
└── main.py           ← nosso agente
```

---

## ✅ Checklist do Dia 1

- [ ] VSCode instalado com as 5 extensões (Error Lens, Ruff, Ty, Claude Code, Even Better TOML)
- [ ] UV instalado e funcionando (`uv --version`)
- [ ] Projeto `agente-seguranca` criado com `uv init`
- [ ] Ruff e Ty instalados como `--dev`
- [ ] `.env`, `.gitignore` e `.env.example` criados
- [ ] `.env` não aparece no `git status`
- [ ] `python-dotenv` e `agno` instalados
- [ ] `main.py` rodando com sucesso (`uv run python main.py`)
- [ ] Entendeu a diferença entre `gpt-5.4-mini`, `gpt-5.4`, `gpt-5.5` e `gpt-5.4-pro`

---

## 📚 Referências

- [UV — Documentação oficial](https://docs.astral.sh/uv/)
- [Ruff — Documentação oficial](https://docs.astral.sh/ruff/)
- [Agno — Documentação](https://docs.agno.com)
- [OpenAI — Modelos disponíveis](https://platform.openai.com/docs/models)
- [Guia Markdown](https://www.markdownguide.org/basic-syntax/)

---

> **Próxima aula (Dia 2):** Modo chat com histórico em memória, system/user/assistant, temperatura, thinking e search — tudo com Agno e exemplos de segurança.
