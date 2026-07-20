# Integração NVIDIA DeepSeek V4 Flash

## Objetivo

Alterar o agente de `agente_com_knowledge.py` para gerar respostas com o modelo
`deepseek-ai/deepseek-v4-flash`, servido pela API da NVIDIA, sem modificar o
comportamento da base de conhecimento.

## Arquitetura

- O modelo de chat será configurado com a classe nativa `Nvidia` do Agno.
- A autenticação do chat será obtida de `NVIDIA_API_KEY` pelo próprio Agno.
- O endpoint continuará sendo o padrão da integração NVIDIA:
  `https://integrate.api.nvidia.com/v1`.
- Como o DeepSeek V4 Flash não oferece um modelo de embeddings, a indexação e a
  consulta vetorial continuarão usando `OpenAIEmbedder` com
  `text-embedding-3-small` e `OPENAI_API_KEY`.
- A configuração da LanceDB, a ingestão de documentos e as instruções do agente
  permanecerão inalteradas.

## Configuração do modelo

O modelo será instanciado com o identificador exato
`deepseek-ai/deepseek-v4-flash`, `temperature=1`, `top_p=0.95` e thinking
habilitado por meio de `extra_body`, seguindo o exemplo publicado pela NVIDIA.
O limite de tokens não será elevado explicitamente, evitando respostas muito
longas por padrão.

## Erros e credenciais

O programa dependerá de duas credenciais no ambiente:

- `NVIDIA_API_KEY` para a geração das respostas;
- `OPENAI_API_KEY` para criar e consultar embeddings.

Erros de credencial e de rede continuarão sendo propagados pelas integrações do
Agno, que fornecem mensagens específicas do provedor.

## Verificação

Um teste automatizado verificará, sem realizar chamadas externas, que o agente
usa a classe `Nvidia`, o ID correto e os parâmetros esperados. Também verificará
que o embedder OpenAI permanece configurado. Por fim, o arquivo será compilado e
os testes do projeto serão executados.

## Fora de escopo

- Migrar embeddings já armazenados na LanceDB.
- Trocar o provedor de embeddings.
- Alterar prompts, documentos ou a pergunta de exemplo.
