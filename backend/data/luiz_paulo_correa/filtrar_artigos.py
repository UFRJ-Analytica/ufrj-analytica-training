"""Gera a colecao de artigos usada pelo agente de pesquisa academica.

Le o dataset ml-arxiv-papers (Hugging Face, colunas 'title' e 'abstract'), seleciona alguns artigos por subtema
e escreve o recorte em artigos_ciencia_de_dados.json.

Roda uma vez. Nao e importado pela aplicacao.

O dataset completo ficou fora do repositorio. coloquei aqui apenas a versao diminuida.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ARQUIVO_SAIDA = Path(__file__).parent / "artigos_ciencia_de_dados.json"
FONTE = "arXiv (via dataset ml-arxiv-papers, Hugging Face)"
ARTIGOS_POR_SUBTEMA = 20

SUBTEMAS: dict[str, list[str]] = {
    "arvores de decisao e ensembles": [
        "random forest",
        "gradient boosting",
        "xgboost",
        "decision tree",
        "ensemble learning",
    ],
    "redes neurais e deep learning": [
        "deep learning",
        "neural network",
        "convolutional network",
        "transformer",
    ],
    "processamento de linguagem natural": [
        "natural language",
        "language model",
        "text classification",
        "word embedding",
    ],
    "clusterizacao": [
        "clustering",
        "k-means",
        "unsupervised learning",
    ],
    "selecao de atributos": [
        "feature selection",
        "feature engineering",
        "dimensionality reduction",
    ],
    "visualizacao de dados": [
        "data visualization",
        "visual analytics",
        "exploratory data analysis",
    ],
    "series temporais": [
        "time series",
        "forecasting",
        "temporal prediction",
    ],
    "grafos e graph learning": [
        "graph neural network",
        "graph learning",
        "graph embedding",
        "node classification",
    ],
}


def normalizar(texto: str) -> str:
    """Minusculas, sem acento e com espacos colapsados."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


def criar_slug(titulo: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalizar(titulo))
    return slug.strip("-")[:70]


def limpar_texto(texto: str) -> str:
    return re.sub(r"\s+", " ", str(texto)).strip()


def selecionar(df: pd.DataFrame) -> list[dict]:
    titulos_normalizados = df["title"].map(normalizar)
    artigos: list[dict] = []
    slugs_usados: set[str] = set()

    for subtema, palavras_chave in SUBTEMAS.items():
        padrao = "|".join(re.escape(p) for p in palavras_chave)
        candidatos = df[titulos_normalizados.str.contains(padrao, regex=True, na=False)]

        escolhidos = 0
        for _, linha in candidatos.iterrows():
            if escolhidos >= ARTIGOS_POR_SUBTEMA:
                break

            titulo = limpar_texto(linha["title"])
            resumo = limpar_texto(linha["abstract"])
            slug = criar_slug(titulo)

            if not slug or slug in slugs_usados or not resumo:
                continue

            titulo_normalizado = normalizar(titulo)
            encontradas = [p for p in palavras_chave if p in titulo_normalizado]

            slugs_usados.add(slug)
            artigos.append(
                {
                    "id": slug,
                    "titulo": titulo,
                    "resumo": resumo,
                    "temas": [subtema, *encontradas],
                    "fonte": FONTE,
                }
            )
            escolhidos += 1

        print(f"{subtema}: {escolhidos} artigos (de {len(candidatos)} candidatos)")

    return artigos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquet", type=Path, help="caminho do ml-arxiv-papers.parquet")
    args = parser.parse_args()

    df = pd.read_parquet(args.parquet)
    print(f"dataset carregado: {len(df)} artigos\n")

    artigos = selecionar(df)

    ARQUIVO_SAIDA.write_text(
        json.dumps(artigos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n{len(artigos)} artigos escritos em {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
