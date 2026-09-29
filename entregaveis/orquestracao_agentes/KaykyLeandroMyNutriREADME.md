# MyNutri — Agente Nutricional com RAG & Tool Calling

O **MyNutri** é uma aplicação assistente baseada em inteligência artificial voltada para nutrição e alimentação. O sistema utiliza **RAG (Retrieval-Augmented Generation)** para consultar tabelas oficiais de composição de alimentos e **Tool Calling via LangGraph** para executar cálculos nutricionais, como o Índice de Massa Corporal (IMC).

---

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Orquestração & Agentes:** LangChain, LangGraph
* **Modelo de Linguagem (LLM):** Google Gemini
* **Backend API:** FastAPI
* **Frontend / Interface:** Streamlit
* **Banco Vetorial (Vector DB):** ChromaDB
* **Embeddings:** Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`)
* **Processamento de Documentos:** PyPDF
* **Containerização:** Docker & Docker Compose

---

## Base de Conhecimento & RAG

O MyNutri utiliza duas tabelas oficiais brasileiras como base contextual para sanar dúvidas sobre alimentos:
* **TACO** — Tabela Brasileira de Composição de Alimentos
* **TBCA** — Tabela Brasileira de Composição de Alimentos

### Fluxo de Ingestão e Processamento

* **Local dos documentos:** `docs/mynutri/`
* **Chunking:** Divisão em blocos de aproximadamente 1000 caracteres com sobreposição (*overlap*) de 200 caracteres.
* **Vector Search:** Os 3 chunks mais relevantes ($k=3$) são recuperados a cada consulta.

```text
[ Pergunta do Usuário ]
          ↓
[ Embedding da Pergunta ]
          ↓
[ Busca Semântica ]
          ↓
[ ChromaDB ]
          ↓
[ Documentos Relevantes ]
          ↓
[ Contexto ] → [ LangGraph / Google Gemini ] → [ Resposta ]
```

---

## Tool Calling

O agente conta com ferramentas internas executadas dinamicamente:

* `calcular_imc(peso_kg, altura_m)`: Ferramenta utilizada pelo LangGraph para realizar o cálculo do IMC a partir do peso e da altura informados pelo usuário. O resultado é posteriormente utilizado pelo LLM na construção da resposta.

---

## Estrutura do Projeto

```text
orquestracao_agentes/
│
├── backend/
│   └── app/
│       ├── agent/
│       │   └── kayky_leandro_agent.py
│       ├── endpoints/
│       │   └── kayky_leandro_endpoint.py
│       └── rag/
│           ├── chroma.py
│           ├── ingest.py
│           ├── retriever.py
│           └── testechroma.py
│
├── docs/
│   └── mynutri/
│       ├── taco.pdf
│       └── tbca.pdf
│
├── pages/
│   └── kayky_leandro_chat.py
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── KaykyLeandroMyNutriREADME.md
└── .gitignore
```

---

## Configuração & Instalação

### 1. Variáveis de Ambiente

Crie um arquivo `.env` dentro do diretório `backend/` para armazenar suas credenciais:

```env
GOOGLE_API_KEY=sua_chave_aqui
```

> **Atenção:** Nunca comite o arquivo `.env` no controle de versão.

### 2. Configuração do Ambiente Python

Na raiz do projeto, execute:

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

## ChromaDB

O projeto inclui um `docker-compose.yml` para executar o ChromaDB em ambiente containerizado, conforme a arquitetura proposta no entregável.

Durante o desenvolvimento local, o RAG também utiliza persistência local do ChromaDB em `chroma_data/`, permitindo executar e testar a aplicação sem depender do container.

```bash
# Subir o container
docker compose up -d

# Verificar se o container está rodando (disponível na porta 8001)
docker ps
```

### 4. Ingestão da Base de Conhecimento

Com o ambiente virtual ativo e o ChromaDB rodando, popule o banco vetorial com os PDFs:

```bash
python backend\app\rag\ingest.py
```

---

## Executando a Aplicação

### 1. Iniciar o Backend (FastAPI)

```bash
cd backend
uvicorn app.main:app --reload
```

* **Documentação Swagger UI:** `http://127.0.0.1:8000/docs`
* **Endpoint Principal:** `POST /agent/mynutri/chat`
* **Payload de Exemplo:**

```json
{
  "message": "O que são proteínas?"
}
```

### 2. Iniciar o Frontend (Streamlit)

Em outro terminal (na raiz do projeto):

```bash
streamlit run pages\kayky_leandro_chat.py
```

O Streamlit se comunica com o backend FastAPI via requisições HTTP REST.

---

## Segurança & Boas Práticas

* Informações sensíveis (como `GOOGLE_API_KEY`) ficam restritas ao arquivo `backend/.env`.
* O diretório `chroma_data/` (utilizado para persistência local do banco) e o ambiente `.venv/` estão configurados no `.gitignore`.

---

## Isenção de Responsabilidade (Disclaimer)

O MyNutri tem caráter estritamente **informativo e educacional** sobre alimentação e nutrição.

O agente **NÃO** deve:
* Diagnosticar doenças ou condições médicas;
* Prescrever dietas ou tratamentos clínicos;
* Substituir a consulta com nutricionistas ou médicos.

*Sempre oriente os usuários a buscarem acompanhamento profissional habilitado para orientações personalizadas.*