# Entrega SGCont — Orquestracao de Agentes

## Entregavel 1 (Agente + FastAPI)

Arquivos:
- `/home/runner/work/ufrj-analytica-training/ufrj-analytica-training/backend/app/agents/sgcont_agent.py`
- `/home/runner/work/ufrj-analytica-training/ufrj-analytica-training/backend/app/endpoints/sgcont_agent.py`

Endpoint:
- `POST /agent/sgcont/chat`
- `GET /agent/sgcont/health`

O agente usa LangGraph com:
- `State` (`messages` + `tool_context`);
- Tool `classificar_pergunta`;
- no de LLM para gerar resposta com contexto da tool.

Se `GEMINI_API_KEY` nao estiver configurada, o agente entra em modo local e retorna orientacoes didaticas.

## Entregavel 2 (Chat Streamlit)

Arquivo:
- `/home/runner/work/ufrj-analytica-training/ufrj-analytica-training/pages/sgcont_chat.py`

Funcionalidades:
- historico persistido em `st.session_state`;
- mensagens do usuario alinhadas a direita e do agente a esquerda;
- area de chat com scroll e limite visual;
- input no rodape via `st.chat_input`;
- loading com `st.spinner`;
- tratamento de erro de conexao, timeout e HTTP.

## Variaveis de ambiente

Criar `backend/.env` local (nao commitar):

```env
GEMINI_API_KEY=sua_chave
SGCONT_MODEL=gemini-2.5-flash
```

A chave pode ser gerada em: https://aistudio.google.com/api-keys
