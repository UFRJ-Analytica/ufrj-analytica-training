Entregável — Orquestração de IA

Objetivo

Nesta capacitação, cada trainee deverá desenvolver uma aplicação de Inteligência Artificial utilizando LLM, LangGraph, FastAPI, Streamlit e ChromaDB.

O projeto será desenvolvido incrementalmente em três entregáveis:

1. Construção de um agente de IA e disponibilização por uma API FastAPI;
2. Construção de uma interface de chat utilizando Streamlit;
3. Implementação de uma base de conhecimento utilizando embeddings, ChromaDB e RAG.

Ao final, a arquitetura deverá seguir aproximadamente o seguinte fluxo:

Usuário
  ↓
Streamlit
  ↓
FastAPI
  ↓
LangGraph Agent
  ├── LLM
  ├── Tools
  └── Retriever
         ↓
      ChromaDB
         ↓
    Base de conhecimento

⸻

Preparação do ambiente

Cada trainee deverá criar uma API Key para utilizar um modelo de linguagem.

Durante a capacitação será demonstrado o uso do Google AI Studio / Gemini API.
Para criar a chave, acesse a página de API Keys do Google AI Studio:

https://aistudio.google.com/api-keys

Crie uma nova API Key, copie o valor gerado e salve somente no arquivo `.env`
local. Não coloque a chave diretamente no código.

Também será apresentado o OpenRouter como alternativa para acesso a diferentes modelos e providers através de uma interface unificada.

As credenciais devem ser armazenadas através de variáveis de ambiente.

Neste projeto, o backend lê o arquivo:

backend/.env

Exemplo de conteúdo:

GEMINI_API_KEY=sua_chave
AGENTE_TESTE_MODEL=gemini-2.5-flash

É proibido realizar commit de API Keys no repositório.

O arquivo .env deve estar presente no .gitignore.

Instalação das dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r backend/requirements.txt
```

Rodar o backend FastAPI, a partir da raiz do projeto:

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

Depois acesse o Swagger em:

http://127.0.0.1:8000/docs

Teste inicial do agente:

```bash
curl -X POST http://127.0.0.1:8000/agent/agente-teste/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explique o entregavel 1"}'
```

Rodar o frontend Streamlit, em outro terminal, a partir da raiz do projeto:

```bash
source .venv/bin/activate
streamlit run app.py
```

A página do agente fica disponível pelo menu lateral do Streamlit ou direto em:

http://127.0.0.1:8501/agente_teste

⸻

Entregável 1 — Agente + FastAPI

Objetivo

Construir um agente utilizando LangGraph e disponibilizá-lo através de um endpoint no backend FastAPI do projeto.

O agente deverá possuir uma responsabilidade específica.

Cada trainee poderá escolher um dos agentes sugeridos neste documento ou propor outro agente.

Requisitos mínimos do agente

O agente deverá possuir:

* modelo LLM configurado;
* System Prompt próprio;
* responsabilidade claramente definida;
* parâmetros do modelo configurados;
* State do LangGraph;
* pelo menos uma Tool criada pelo trainee;
* fluxo implementado utilizando LangGraph;
* entrada de mensagens do usuário;
* resposta gerada pelo agente.

O código do agente deve ficar separado da camada HTTP.

Estrutura sugerida:

backend/
└── app/
    ├── agents/
    │   └── nome_sobrenome_agent.py
    │
    └── endpoints/
        └── nome_sobrenome_agent.py

O arquivo dentro de agents/ será responsável pela implementação e configuração do agente.

O arquivo dentro de endpoints/ será responsável por disponibilizar o agente através do FastAPI.

Endpoint

Criar pelo menos um endpoint:

POST /agent/<nome-do-agente>/chat

Exemplo de request:

{
  "message": "Analise estes dados para mim"
}

Exemplo de response:

{
  "response": "Resultado produzido pelo agente."
}

O endpoint deverá ser testável inicialmente através do Swagger do FastAPI.

Antes de iniciar o frontend, certifique-se de que o agente funciona diretamente pelo backend.

⸻

Entregável 2 — Interface de Chat

Objetivo

Construir uma página Streamlit que permita conversar com o agente criado no Entregável 1.

Cada trainee deverá criar seu próprio arquivo seguindo obrigatoriamente o padrão:

pages/nome_sobrenome_chat.py

Exemplo:

pages/joao_silva_chat.py

Requisitos da interface

A página deverá possuir:

* título identificando o agente;
* área contendo o histórico da conversa;
* mensagens do agente alinhadas visualmente à esquerda;
* mensagens do usuário alinhadas visualmente à direita;
* campo de texto na parte inferior;
* botão para envio da mensagem;
* campo de entrada fixo na parte inferior da interface;
* área de mensagens com scroll;
* limite visual da área de mensagens para impedir crescimento indefinido da página;
* indicador de carregamento enquanto o agente processa a solicitação;
* tratamento básico de erro caso o backend esteja indisponível.

O histórico da conversa deverá permanecer disponível durante a sessão utilizando:

st.session_state

Estrutura conceitual:

[
    {
        "role": "user",
        "content": "Olá"
    },
    {
        "role": "assistant",
        "content": "Olá! Como posso ajudar?"
    }
]

Comunicação com backend

O Streamlit NÃO deverá executar diretamente o agente.

O fluxo obrigatório será:

Streamlit
    ↓
HTTP Request
    ↓
FastAPI
    ↓
LangGraph
    ↓
LLM
    ↓
FastAPI
    ↓
Streamlit

Dessa forma, frontend e backend permanecem desacoplados.

⸻

Entregável 3 — ChromaDB + Embeddings + RAG

Objetivo

Adicionar uma base de conhecimento ao agente utilizando uma Vector Database.

Será utilizado o ChromaDB executado através do Docker.

O trainee deverá selecionar conteúdos relacionados ao domínio do agente criado no Entregável 1.

Exemplos:

Agente Financeiro
↓
documentos sobre finanças
Agente de Filmes
↓
dataset ou documentos sobre filmes
Agente de Dados
↓
documentação de Pandas
Agente de Saúde
↓
documentos públicos sobre saúde

⸻

ChromaDB

O ChromaDB deverá ser executado através de container Docker.

O trainee deverá pesquisar a imagem oficial do ChromaDB e entender:

* qual imagem será utilizada;
* qual porta será exposta;
* como executar o container;
* como configurar persistência;
* como conectar a aplicação Python ao ChromaDB.

Não basta executar o banco.

O agente deverá efetivamente recuperar informações armazenadas nele.

⸻

Pipeline de ingestão

O conteúdo escolhido deverá passar pelo seguinte pipeline:

Documento
   ↓
Document Loader
   ↓
Text Splitting
   ↓
Chunks
   ↓
Embedding Model
   ↓
Vetores
   ↓
ChromaDB

Cada chunk deverá possuir, quando aplicável:

texto
embedding
metadata
fonte

O trainee deverá definir uma estratégia de divisão dos documentos.

Exemplo conceitual:

Documento com 20 páginas
        ↓
Text Splitter
        ↓
Chunk 1
Chunk 2
Chunk 3
...
        ↓
Embeddings
        ↓
ChromaDB

⸻

Retrieval

Após a ingestão, a aplicação deverá permitir uma busca semântica.

Fluxo:

Pergunta do usuário
        ↓
Embedding da pergunta
        ↓
Vector Search
        ↓
ChromaDB
        ↓
Top K documentos

O trainee deverá demonstrar que uma pergunta semanticamente relacionada ao conteúdo recupera documentos relevantes.

⸻

RAG

Após validar o Retrieval, ele deverá ser conectado ao agente.

Fluxo final:

Pergunta
   ↓
Retriever
   ↓
ChromaDB
   ↓
Documentos relevantes
   ↓
Contexto
   ↓
LangGraph Agent
   ↓
LLM
   ↓
Resposta

O agente deverá utilizar os documentos recuperados como contexto para produzir sua resposta.

Quando a resposta depender da base de conhecimento, o agente não deverá inventar informações ausentes nos documentos.

⸻

10 sugestões de agentes

Cada trainee deverá escolher um agente diferente sempre que possível.

1. Agente de Análise de Dados

Recebe perguntas sobre análise de dados e auxilia na interpretação de datasets.

Possíveis Tools:

calcular_media
calcular_mediana
calcular_estatisticas

Base RAG sugerida:

documentação de Pandas
material da capacitação

2. Agente de Filmes

Recomenda e responde perguntas sobre filmes.

Possíveis Tools:

buscar_filme
filtrar_por_genero
calcular_avaliacao_media

Base RAG sugerida:

dataset de filmes
sinopses
informações públicas

3. Agente de Livros

Auxilia na descoberta e análise de livros.

Possíveis Tools:

buscar_livro
buscar_autor
filtrar_genero

Base RAG:

catálogo de livros
resumos
documentos sobre literatura

4. Agente Financeiro Educacional

Explica conceitos financeiros e realiza cálculos simples.

Possíveis Tools:

calcular_juros
calcular_retorno
calcular_variacao_percentual

Base RAG:

materiais educacionais sobre finanças
documentação pública

5. Agente de Python

Assistente especializado em programação Python.

Possíveis Tools:

consultar_exemplo
analisar_estrutura
buscar_documentacao

Base RAG:

documentação Python
PEPs selecionadas
material da capacitação

6. Agente de FastAPI

Assistente especializado em desenvolvimento de APIs utilizando FastAPI.

Possíveis Tools:

buscar_endpoint
buscar_exemplo
consultar_documentacao

Base RAG:

documentação do FastAPI
material da capacitação

7. Agente de Docker

Assistente especializado em conceitos e comandos Docker.

Possíveis Tools:

buscar_comando
explicar_dockerfile
explicar_compose

Base RAG:

documentação Docker
material da capacitação DevOps

8. Agente de Games

Assistente para pesquisa e recomendação de jogos.

Possíveis Tools:

buscar_jogo
filtrar_genero
filtrar_plataforma

Base RAG:

dataset de jogos
descrições
reviews públicas

9. Agente de Pesquisa Acadêmica

Auxilia na consulta de uma pequena coleção de artigos ou materiais acadêmicos.

Possíveis Tools:

buscar_documento
buscar_por_autor
buscar_por_tema

Base RAG:

artigos científicos
resumos
material acadêmico

10. Agente de Indicadores Públicos

Auxilia na interpretação de indicadores provenientes de datasets públicos.

Possíveis Tools:

calcular_indicador
comparar_periodos
buscar_localidade

Base RAG:

documentação do dataset
dicionário de dados
metodologia dos indicadores

⸻

Estrutura final esperada

Ao final dos três entregáveis, a aplicação deverá possuir aproximadamente:

project/
│
├── pages/
│   └── nome_sobrenome_chat.py
│
├── backend/
│   └── app/
│       ├── agents/
│       │   └── nome_sobrenome_agent.py
│       │
│       └── endpoints/
│           └── nome_sobrenome_agent.py
│
├── docker-compose.yml
│
└── .env

Além disso:

Docker
└── ChromaDB

⸻

Critérios de avaliação

Entregável 1

Será avaliado:

* funcionamento do agente;
* organização do código;
* qualidade do System Prompt;
* configuração do modelo;
* utilização correta do LangGraph;
* implementação de State;
* implementação de pelo menos uma Tool;
* funcionamento do endpoint FastAPI;
* separação entre agente e endpoint.

Entregável 2

Será avaliado:

* funcionamento da página Streamlit;
* integração real com o backend;
* histórico da conversa;
* organização visual das mensagens;
* alinhamento usuário/agente;
* área de mensagens com scroll;
* input na parte inferior;
* tratamento de loading e erros;
* utilização adequada de st.session_state.

Entregável 3

Será avaliado:

* execução do ChromaDB via Docker;
* persistência dos dados;
* escolha adequada da base de conhecimento;
* processamento dos documentos;
* geração de embeddings;
* armazenamento dos vetores;
* funcionamento da busca semântica;
* implementação do Retriever;
* integração do Retrieval com o LangGraph;
* funcionamento do RAG.

⸻

Regras

1. Não realizar commit de API Keys ou outros secrets.
2. Não colocar o agente diretamente dentro da página Streamlit.
3. O frontend deverá consumir o backend através de HTTP.
4. O agente deverá utilizar LangGraph.
5. O ChromaDB deverá ser executado através de Docker.
6. O Entregável 3 deverá possuir Retrieval funcional; apenas subir o ChromaDB não é suficiente.
7. O código deverá seguir o padrão de nomes definido para cada trainee.
8. Cada trainee deverá compreender e conseguir explicar o código entregue.
9. Bibliotecas adicionais são permitidas quando justificadas.
10. O projeto deve continuar executável para os demais membros do repositório.

⸻

Resultado esperado

Ao final da capacitação, cada trainee deverá ser capaz de explicar e demonstrar:

LLM
↓
Prompt Engineering
↓
System Prompt
↓
Context Window
↓
LangChain
↓
LangGraph
↓
State
↓
Agent
↓
Tool Calling
↓
FastAPI
↓
Streamlit
↓
Embeddings
↓
Vector Database
↓
Retrieval
↓
RAG

O objetivo não é apenas construir um chatbot.

O objetivo é compreender como orquestrar componentes de IA para construir uma aplicação baseada em agentes, ferramentas, memória e conhecimento externo.
