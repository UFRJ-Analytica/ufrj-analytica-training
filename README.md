# Analytica Training

Base inicial de um app Streamlit para apresentar equipe e projetos do treinamento.

<div align="center">
  <img src="media/diagrama-importante.png" width="250" alt="Diagrama importante sobre o projeto">
</div>

## Como rodar

Instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r backend/requirements.txt
```

Para o agente Gemini, crie `backend/.env` com:

```env
GEMINI_API_KEY=sua_chave
AGENTE_TESTE_MODEL=gemini-2.5-flash
```

Rode o backend FastAPI em um terminal:

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

Swagger do backend:

```text
http://127.0.0.1:8000/docs
```

Rode o Streamlit em outro terminal, a partir da raiz do projeto:

```bash
streamlit run app.py
```

Página do agente:

```text
http://127.0.0.1:8501/agente_teste
```

## Estrutura

- `app.py`: home com visao geral.
- `pages/1_Equipe.py`: pagina de membros com filtros.
- `pages/2_Projetos.py`: pagina de projetos com status e progresso.
- `pages/agente_teste.py`: chat do agente de teste.
- `backend/app/agents/agente_teste_agent.py`: configuracao do agente.
- `backend/app/endpoints/agente_endpoint_teste.py`: endpoint FastAPI do agente.
- `data/*.csv`: dados de exemplo.


# Contiue
# Continue
