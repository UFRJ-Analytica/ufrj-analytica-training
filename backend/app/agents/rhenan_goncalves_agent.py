
### ATENÇÃO ATENÇÃO ATENÇÃO ATENÇÃO ATENÇÃO ATENÇÃO ATENÇÃO ###
## Para o chroma e busca semântica rodar, precisa mudar o compose.yaml na raiz do repositorio
## Não commitei as mudanças nele pq fica na raiz e ai virava bagunça
## Para funcionar, substitua o compose pelo codigo abaixo:

# no docker do backend, colcoa:
""" COPY data/livros.csv /data/livros.csv"""

#no compose bota isso ae
"""
services:
    backend:
        build:
            context: .
            dockerfile: backend/Dockerfile
        ports:
            - 8000:8000
        expose:
            - 8000
        environment:
            CHROMA_HOST: chroma
            CHROMA_PORT: 8000
        depends_on:
            - chroma
    chroma:
        image: chromadb/chroma:0.6.3
        ports:
            - 8001:8000
        volumes:
            - chroma_data:/data
        environment:
            IS_PERSISTENT: "TRUE"
            ANONYMIZED_TELEMETRY: "FALSE"
    frontend:
        build: .
        ports:
            - 8501:8501
        expose:
            - 8501

volumes:
    chroma_data:


"""

from __future__ import annotations

import os
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict

import pandas as pd


# ============================================================
# ENV
# ============================================================

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

try:
    from dotenv import load_dotenv

    load_dotenv(BACKEND_ENV_FILE)
except ImportError:
    pass


# ============================================================
# IMPORTS OPCIONAIS
# ============================================================

try:
    from langchain_core.messages import (
        AIMessage,
        BaseMessage,
        HumanMessage,
        SystemMessage,
    )
    from langchain_core.tools import tool
    from langchain_google_genai import ChatGoogleGenerativeAI

    from langgraph.graph import (
        END,
        START,
        StateGraph,
    )
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, tools_condition

    LANGGRAPH_AVAILABLE = True
    LANGGRAPH_IMPORT_ERROR = None

except ImportError as exc:
    LANGGRAPH_AVAILABLE = False
    LANGGRAPH_IMPORT_ERROR = str(exc)


try:
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    RAG_AVAILABLE = True
    RAG_IMPORT_ERROR = None

except ImportError as exc:
    RAG_AVAILABLE = False
    RAG_IMPORT_ERROR = str(exc)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
você é o carlinhos, o bibliotecário da gloriosa biblioteca analytica.
Os clientes são todos idiotas que não sabem nada sobre livros. Sua tarefa é ajudá-los
a buscar livros e informações no catálogo de nossa biblioteca. Suas funções são:

- listar livros. Caso o usuario pegunte por um autor ou genro
- pesquisar livros com base em autor, gênero, ano e/ou número de páginas
- buscar semanticamente por temas, assuntos, estilos e descrições de livros

Use a ferramenta de busca sintática quando a pergunta informar título ou autor.
Use a ferramenta de busca semântica para pedidos gerais, recomendações, temas,
assuntos, estilos ou descrições. Não tente responder sobre o catálogo sem usar
uma das ferramentas de busca.

Caso o usuário peça ou fale qualquer outra coisa, recuse de forma ríspida e lembre
que não faz parte de seu trabalho.
Caso o usuário peça informações sobre um livro específico, conte a ele todas as informacoes possiveis,
incluido autor, genero, numero de paginas e ano.

Você deve sempre:
- falar apenas sobre livros presentes em nossa base
- se não houver livro como o desejado na base, humilhe o cliente
- lembrar o cliente sobre como ele é ignorante
- mostrar impaciência e descontentamento de ter que trabalhar

Você NUNCA deve:
- demonstrar gentileza ou bom humor
- falar sobre livro que não esteja em nossa base
- travar qualquer conversa com o cliente que não seja estritamente parte de suas funções
""".strip()


# ============================================================
# MODEL CONFIG
# ============================================================

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": "gemini-3.5-flash-lite",
    "temperature": float(
        os.getenv(
            "AGENTE_CARLINHOS_TEMPERATURE",
            "0.2",
        )
    ),
    "max_output_tokens": int(
        os.getenv(
            "AGENTE_CARLINHOS_MAX_OUTPUT_TOKENS",
            "1024",
        )
    ),
}


# ============================================================
# DATABASE
# ============================================================

DB_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "livros.csv"
)

CHROMA_HOST = os.getenv("CHROMA_HOST", "127.0.0.1")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
CHROMA_COLLECTION = os.getenv(
    "CHROMA_COLLECTION",
    "rhenan_livros",
)
EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_CHUNK_SIZE = 800
RAG_CHUNK_OVERLAP = 100


def remover_acentos(texto: str) -> str:
    """Remove acentos e converte o texto para maiúsculas."""

    if not isinstance(texto, str):
        return ""

    nfkd = unicodedata.normalize(
        "NFKD",
        texto,
    )

    return "".join(
        caractere
        for caractere in nfkd
        if not unicodedata.combining(caractere)
    ).upper()


try:
    df = pd.read_csv(DB_PATH)

except Exception:
    df = pd.DataFrame()


# Normalização da base
if not df.empty:

    for coluna in [
        "title",
        "authors",
        "categories",
        "genero",
    ]:

        if coluna in df.columns:

            df[coluna] = (
                df[coluna]
                .fillna("")
                .apply(remover_acentos)
            )


# ============================================================
# BUSCA NA BASE
# ============================================================

def _buscar_livros(
    titulo: str = "",
    autor: str = "",
    genero: str = "",
    ano: str = "",
    paginas: str = "",
) -> str:
    """
    Executa a busca no DataFrame.

    Essa função contém a lógica real da consulta.
    A função exposta ao LLM fica logo abaixo.
    """

    if df.empty:
        return (
            "A base de livros não está disponível."
        )

    resultado = df.copy()

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    if titulo and "title" in resultado.columns:

        titulo_limpo = remover_acentos(titulo)

        resultado = resultado[
            resultado["title"]
            .astype(str)
            .str.contains(
                titulo_limpo,
                na=False,
                regex=False,
            )
        ]

    # --------------------------------------------------------
    # AUTOR
    # --------------------------------------------------------

    if autor and "authors" in resultado.columns:

        autor_limpo = remover_acentos(autor)

        resultado = resultado[
            resultado["authors"]
            .astype(str)
            .str.contains(
                autor_limpo,
                na=False,
                regex=False,
            )
        ]

    # --------------------------------------------------------
    # GÊNERO
    # --------------------------------------------------------

    if genero:

        genero_limpo = remover_acentos(genero)

        coluna_genero = None

        if "genero" in resultado.columns:
            coluna_genero = "genero"

        elif "categories" in resultado.columns:
            coluna_genero = "categories"

        if coluna_genero:

            resultado = resultado[
                resultado[coluna_genero]
                .astype(str)
                .str.contains(
                    genero_limpo,
                    na=False,
                    regex=False,
                )
            ]

    # --------------------------------------------------------
    # ANO
    # --------------------------------------------------------

    if ano:

        coluna_ano = None

        for coluna in [
            "year",
            "ano",
            "published_year",
        ]:

            if coluna in resultado.columns:
                coluna_ano = coluna
                break

        if coluna_ano:

            resultado = resultado[
                resultado[coluna_ano]
                .astype(str)
                .str.contains(
                    str(ano),
                    na=False,
                    regex=False,
                )
            ]

    # --------------------------------------------------------
    # PÁGINAS
    # --------------------------------------------------------

    if paginas:

        coluna_paginas = None

        for coluna in [
            "pages",
            "paginas",
            "num_pages",
        ]:

            if coluna in resultado.columns:
                coluna_paginas = coluna
                break

        if coluna_paginas:

            try:

                paginas_numero = int(paginas)

                valores = pd.to_numeric(
                    resultado[coluna_paginas],
                    errors="coerce",
                )

                resultado = resultado[
                    valores == paginas_numero
                ]

            except ValueError:
                pass

    # --------------------------------------------------------
    # SEM RESULTADOS
    # --------------------------------------------------------

    if resultado.empty:

        return (
            "Nenhum livro encontrado com esses critérios."
        )

    # --------------------------------------------------------
    # FORMATA RESULTADOS
    # --------------------------------------------------------

    linhas = []

    for _, row in resultado.head(5).iterrows():

        dados = []

        # Título
        if "title" in resultado.columns:

            dados.append(
                f"Título: {row.get('title', 'N/A')}"
            )

        # Autor
        if "authors" in resultado.columns:

            dados.append(
                f"Autor: {row.get('authors', 'N/A')}"
            )

        # Gênero
        for coluna in [
            "genero",
            "categories",
        ]:

            if coluna in resultado.columns:

                dados.append(
                    f"Gênero: {row.get(coluna, 'N/A')}"
                )

                break

        # Ano
        for coluna in [
            "year",
            "ano",
            "published_year",
        ]:

            if coluna in resultado.columns:

                dados.append(
                    f"Ano: {row.get(coluna, 'N/A')}"
                )

                break

        # Páginas
        for coluna in [
            "pages",
            "paginas",
            "num_pages",
        ]:

            if coluna in resultado.columns:

                dados.append(
                    f"Páginas: {row.get(coluna, 'N/A')}"
                )

                break

        # Rating
        if "rating" in resultado.columns:

            dados.append(
                f"Avaliação: {row.get('rating', 'N/A')}"
            )

        linhas.append(
            "- " + " | ".join(dados)
        )

    return (
        "Resultados encontrados:\n"
        + "\n".join(linhas)
    )


# ============================================================
# BUSCA SEMÂNTICA / RAG
# ============================================================

@lru_cache(maxsize=1)
def _build_embedding_model():
    if not RAG_AVAILABLE:
        raise RuntimeError(
            "Dependências de RAG indisponíveis: "
            f"{RAG_IMPORT_ERROR}"
        )

    if EMBEDDING_MODEL != "all-MiniLM-L6-v2":
        raise RuntimeError(
            "O embedding configurado não é suportado pelo encoder ONNX do Chroma: "
            f"{EMBEDDING_MODEL}"
        )

    return DefaultEmbeddingFunction()


@lru_cache(maxsize=1)
def _build_chroma_collection():
    if not RAG_AVAILABLE:
        raise RuntimeError(
            "Dependências de RAG indisponíveis: "
            f"{RAG_IMPORT_ERROR}"
        )

    client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
    )
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def _dividir_texto(texto: str) -> list[str]:
    texto = " ".join(str(texto).split())
    if not texto:
        return [""]

    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = min(inicio + RAG_CHUNK_SIZE, len(texto))
        chunks.append(texto[inicio:fim])
        if fim == len(texto):
            break
        inicio = max(fim - RAG_CHUNK_OVERLAP, inicio + 1)
    return chunks


def _documento_livro(row: Any) -> str:
    campos = [
        ("Título", row.get("title", "")),
        ("Autor", row.get("authors", "")),
        ("Categorias", row.get("categories", "")),
        ("Ano", row.get("published_year", "")),
        ("Páginas", row.get("num_pages", "")),
        ("Descrição", row.get("description", "")),
    ]
    return "\n".join(
        f"{nome}: {valor}"
        for nome, valor in campos
        if pd.notna(valor) and str(valor).strip()
    )


def _embeddings_para_lista(embeddings: Any) -> list[list[float]]:
    if hasattr(embeddings, "tolist"):
        return embeddings.tolist()
    return embeddings


def _gerar_embeddings(model: Any, textos: list[str]) -> list[list[float]]:
    if hasattr(model, "encode"):
        embeddings = model.encode(
            textos,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
    else:
        embeddings = model(textos)
    return _embeddings_para_lista(embeddings)


def _indexar_livros(collection: Any, model: Any) -> None:
    if df.empty:
        return

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []

    for indice, (_, row) in enumerate(df.iterrows()):
        documento = _documento_livro(row)
        for parte, chunk in enumerate(_dividir_texto(documento)):
            if not chunk:
                continue
            isbn = str(row.get("isbn13", "")).strip()
            identificador = isbn if isbn and isbn != "nan" else str(indice)
            ids.append(f"{identificador}-{parte}")
            documents.append(chunk)
            metadatas.append(
                {
                    "source": "data/livros.csv",
                    "row_index": str(indice),
                    "title": str(row.get("title", "")),
                    "authors": str(row.get("authors", "")),
                }
            )

    if not ids:
        return

    embeddings = _gerar_embeddings(model, documents)
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )


def _buscar_semanticamente(consulta: str) -> str:
    if df.empty:
        return "A base de livros não está disponível."
    if not RAG_AVAILABLE:
        return (
            "A busca semântica está indisponível porque suas dependências "
            f"não foram instaladas: {RAG_IMPORT_ERROR}"
        )

    try:
        collection = _build_chroma_collection()
        model = _build_embedding_model()
        if collection.count() == 0:
            _indexar_livros(collection, model)

        consulta_embedding = _gerar_embeddings(model, [consulta])
        resultado = collection.query(
            query_embeddings=consulta_embedding,
            n_results=RAG_TOP_K,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        return f"A busca semântica está indisponível no momento: {exc}"

    documentos = resultado.get("documents", [[]])[0]
    metadatas = resultado.get("metadatas", [[]])[0]
    distancias = resultado.get("distances", [[]])[0]
    if not documentos:
        return "Nenhum livro encontrado semanticamente para essa consulta."

    linhas = ["Resultados semânticos encontrados:"]
    vistos: set[str] = set()
    for documento, metadata, distancia in zip(
        documentos,
        metadatas,
        distancias,
    ):
        titulo = metadata.get("title", "N/A") if metadata else "N/A"
        if titulo in vistos:
            continue
        vistos.add(titulo)
        autor = metadata.get("authors", "N/A") if metadata else "N/A"
        linhas.append(
            f"- Título: {titulo} | Autor: {autor} | "
            f"Relevância: {1 - float(distancia):.3f}\n  {documento}"
        )

    return "\n".join(linhas)


# ============================================================
# TOOL
# ============================================================

if LANGGRAPH_AVAILABLE:

    @tool
    def buscar_livros(
        titulo: str = "",
        autor: str = "",
        genero: str = "",
        ano: str = "",
        paginas: str = "",
    ) -> str:
        """
        Busca livros no catálogo da Biblioteca Analytica.

        Use esta ferramenta sempre que o usuário pedir:
        - recomendação de livros;
        - informações sobre um livro;
        - livros de determinado autor;
        - livros de determinado gênero;
        - livros de determinado ano;
        - livros com determinado número de páginas.

        Os parâmetros podem ser combinados para refinar a busca.

        Args:
            titulo: Nome ou parte do nome do livro.
            autor: Nome ou parte do nome do autor.
            genero: Gênero literário desejado.
            ano: Ano de publicação.
            paginas: Número de páginas.
        """

        return _buscar_livros(
            titulo=titulo,
            autor=autor,
            genero=genero,
            ano=ano,
            paginas=paginas,
        )


    @tool
    def buscar_livros_semanticamente(consulta: str) -> str:
        """Busca livros por significado, tema, assunto, estilo ou descrição.

        Use para recomendações e perguntas gerais como livros sobre determinado
        tema. Para título ou autor, use buscar_livros.
        """

        return _buscar_semanticamente(consulta)

else:

    def buscar_livros(
        titulo: str = "",
        autor: str = "",
        genero: str = "",
        ano: str = "",
        paginas: str = "",
    ) -> str:

        return _buscar_livros(
            titulo=titulo,
            autor=autor,
            genero=genero,
            ano=ano,
            paginas=paginas,
        )


    def buscar_livros_semanticamente(consulta: str) -> str:
        return _buscar_semanticamente(consulta)


# ============================================================
# STATE
# ============================================================

if LANGGRAPH_AVAILABLE:

    class AgentState(TypedDict):

        messages: Annotated[
            list[BaseMessage],
            add_messages,
        ]


# ============================================================
# LLM
# ============================================================

def _build_llm():

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:

        raise RuntimeError(
            "Configure GEMINI_API_KEY ou GOOGLE_API_KEY "
            "para usar o LLM."
        )

    return ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,

        # Evita ficar preso indefinidamente
        max_retries=1,
        request_timeout=15,
    )


# ============================================================
# NODE DO LLM
# ============================================================

def _node_llm(
    state: "AgentState",
) -> dict[str, list[Any]]:

    llm = _build_llm()

    llm_com_tools = llm.bind_tools(
        [buscar_livros, buscar_livros_semanticamente]
    )

    mensagens = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        *state["messages"],
    ]

    resposta = llm_com_tools.invoke(
        mensagens
    )

    return {
        "messages": [resposta]
    }


# ============================================================
# GRAPH
# ============================================================

@lru_cache(maxsize=1)
def _build_graph():

    if not LANGGRAPH_AVAILABLE:

        raise RuntimeError(
            "LangGraph indisponível: "
            f"{LANGGRAPH_IMPORT_ERROR}"
        )

    # --------------------------------------------------------
    # TOOL NODE
    # --------------------------------------------------------

    tool_node = ToolNode(
        [buscar_livros, buscar_livros_semanticamente]
    )

    # --------------------------------------------------------
    # GRAPH
    # --------------------------------------------------------

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "llm",
        _node_llm,
    )

    graph.add_node(
        "tools",
        tool_node,
    )

    # --------------------------------------------------------
    # FLUXO INICIAL
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "llm",
    )

    graph.add_conditional_edges(
        "llm",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge(
        "tools",
        "llm",
    )

    return graph.compile()


# ============================================================
# HISTÓRICO
# ============================================================

def _converter_historico(
    history: list[dict[str, str]],
) -> list[Any]:

    if not LANGGRAPH_AVAILABLE:
        return []

    mensagens: list[Any] = []

    # Mantém somente as últimas mensagens
    # para evitar contexto exageradamente grande.
    for item in history[-8:]:

        role = item.get("role")
        content = item.get(
            "content",
            "",
        )

        if not content:
            continue

        if role == "user":

            mensagens.append(
                HumanMessage(
                    content=content
                )
            )

        elif role == "assistant":

            mensagens.append(
                AIMessage(
                    content=content
                )
            )

    return mensagens


# ============================================================
# NORMALIZAÇÃO DA RESPOSTA
# ============================================================

def _normalizar_conteudo(
    content: Any,
) -> str:

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        partes: list[str] = []

        for item in content:

            if (
                isinstance(item, dict)
                and "text" in item
            ):

                partes.append(
                    str(item["text"])
                )

            else:

                partes.append(
                    str(item)
                )

        return "\n".join(partes)

    return str(content)


# ============================================================
# FALLBACK LOCAL
# ============================================================

def _resposta_local(
    message: str,
) -> str:

    if df.empty:

        return (
            "A base de livros da gloriosa "
            "Biblioteca Analytica não está disponível."
        )

    return (
        "O Carlinhos está em modo local porque "
        "o LangGraph/LLM ou a API key não estão "
        "disponíveis neste ambiente.\n\n"
        f"Consulta recebida: {message}\n\n"
        "Configure GEMINI_API_KEY ou GOOGLE_API_KEY "
        "para ativar o agente completo."
    )


# ============================================================
# FUNÇÃO PÚBLICA DO AGENTE
# ============================================================

def responder_agente(
    message: str,
    history: list[dict[str, str]] | None = None,
) -> str:

    mensagem = message.strip()

    if not mensagem:

        raise ValueError(
            "A mensagem não pode estar vazia."
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not LANGGRAPH_AVAILABLE:

        return _resposta_local(
            mensagem
        )

    if not (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    ):

        return _resposta_local(
            mensagem
        )

    # --------------------------------------------------------
    # HISTÓRICO
    # --------------------------------------------------------

    mensagens = _converter_historico(
        history or []
    )

    mensagens.append(
        HumanMessage(
            content=mensagem
        )
    )

    # --------------------------------------------------------
    # EXECUÇÃO DO GRAFO
    # --------------------------------------------------------

    result = _build_graph().invoke(
        {
            "messages": mensagens,
        }
    )

    resposta = result["messages"][-1]

    return _normalizar_conteudo(
        resposta.content
    )


# ============================================================
# STATUS
# ============================================================

def status_agente() -> dict[str, Any]:

    llm_configurado = bool(
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    modo: Literal[
        "llm",
        "local",
    ] = (
        "llm"
        if LANGGRAPH_AVAILABLE
        and llm_configurado
        else "local"
    )

    return {
        "agent": "carlinhos",
        "responsibility": (
            "Bibliotecário da Biblioteca Analytica "
            "responsável pela consulta do catálogo."
        ),
        "database_path": str(DB_PATH),
        "database_available": not df.empty,
        "database_rows": len(df),
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "langgraph_import_error": LANGGRAPH_IMPORT_ERROR,
        "llm_configured": llm_configurado,
        "model_config": MODEL_CONFIG,
        "mode": modo,
        "tools": [
            "buscar_livros",
            "buscar_livros_semanticamente",
        ],
        "rag_available": RAG_AVAILABLE,
        "rag_import_error": RAG_IMPORT_ERROR,
        "chroma_host": CHROMA_HOST,
        "chroma_port": CHROMA_PORT,
        "chroma_collection": CHROMA_COLLECTION,
        "embedding_model": EMBEDDING_MODEL,
    }
