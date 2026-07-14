"""
get_ibge_dataframes.py

Script starter para o módulo de Banco de Dados 1.

Objetivo:
- Consumir APIs públicas do IBGE;
- Criar DataFrames com dados reais;
- Salvar arquivos CSV na pasta data/raw dentro da pasta banco_de_dados;
- NÃO criar banco;
- NÃO criar tabelas;
- NÃO definir o modelo relacional final.

Estrutura esperada:

ufrj-analytica-training/
  entregaveis/
    banco_de_dados/
      get_ibge_dataframes.py
      load_raw_to_sqlite.py
      data/
        raw/
          regioes.csv
          estados.csv
          municipios.csv
          populacao_municipal.csv
          municipios_com_populacao.csv

Fontes:
- IBGE Localidades: regiões, estados e municípios
- SIDRA/IBGE tabela 6579: população residente estimada por município
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import requests


# =========================================================
# CAMINHOS DO PROJETO
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "data" / "raw"


# =========================================================
# FONTES DE DADOS
# =========================================================

IBGE_LOCALIDADES_BASE = "https://servicodados.ibge.gov.br/api/v1/localidades"

SIDRA_POPULACAO_URL = (
    "https://apisidra.ibge.gov.br/values/"
    "t/6579/n6/all/v/9324/p/last?formato=json"
)


def get_json(url: str) -> Any:
    """Faz uma requisição GET e retorna o JSON."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def get_regioes_df() -> pd.DataFrame:
    """Baixa regiões brasileiras da API de Localidades do IBGE."""
    data = get_json(f"{IBGE_LOCALIDADES_BASE}/regioes")

    rows = []

    for item in data:
        rows.append(
            {
                "id_regiao": item.get("id"),
                "sigla_regiao": item.get("sigla"),
                "nome_regiao": item.get("nome"),
            }
        )

    return pd.DataFrame(rows)


def get_estados_df() -> pd.DataFrame:
    """Baixa UFs brasileiras da API de Localidades do IBGE."""
    data = get_json(f"{IBGE_LOCALIDADES_BASE}/estados")

    rows = []

    for item in data:
        regiao = item.get("regiao", {})

        rows.append(
            {
                "id_uf": item.get("id"),
                "sigla_uf": item.get("sigla"),
                "nome_uf": item.get("nome"),
                "id_regiao": regiao.get("id"),
                "sigla_regiao": regiao.get("sigla"),
                "nome_regiao": regiao.get("nome"),
            }
        )

    return pd.DataFrame(rows)


def get_municipios_df() -> pd.DataFrame:
    """Baixa municípios brasileiros da API de Localidades do IBGE."""
    data = get_json(f"{IBGE_LOCALIDADES_BASE}/municipios")

    rows = []

    for item in data:
        microrregiao = item.get("microrregiao", {})

        if microrregiao is None:
            print(
                f"Microrregião ausente para o município "
                f"{item.get('nome')} | ID: {item.get('id')}"
            )
            continue

        mesorregiao = microrregiao.get("mesorregiao", {})
        uf = mesorregiao.get("UF", {})
        regiao = uf.get("regiao", {})

        rows.append(
            {
                "id_municipio": item.get("id"),
                "nome_municipio": item.get("nome"),
                "id_uf": uf.get("id"),
                "sigla_uf": uf.get("sigla"),
                "nome_uf": uf.get("nome"),
                "id_regiao": regiao.get("id"),
                "sigla_regiao": regiao.get("sigla"),
                "nome_regiao": regiao.get("nome"),
            }
        )

    return pd.DataFrame(rows)


def parse_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def parse_float(value: Any) -> float | None:
    try:
        text = str(value).strip().replace(",", ".")
        if text in {"", "-", "...", "X"}:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def find_municipio_id(row: dict[str, Any], valid_ids: set[int]) -> int | None:
    """
    A API do SIDRA retorna dimensões em colunas como D1C, D2C, D3C etc.

    Nesta tabela, o código do município costuma vir em D1C.
    Ainda assim, deixamos uma busca mais flexível para evitar quebra
    caso a estrutura mude levemente.
    """
    preferred_keys = ["D1C", "D2C", "D3C", "D4C"]

    for key in preferred_keys:
        candidate = parse_int(row.get(key))
        if candidate in valid_ids:
            return candidate

    for key, value in row.items():
        if key.startswith("D") and key.endswith("C"):
            candidate = parse_int(value)
            if candidate in valid_ids:
                return candidate

    return None


def find_ano(row: dict[str, Any]) -> int | None:
    """
    Procura um ano nas dimensões retornadas pelo SIDRA.

    Nesta tabela, o ano costuma aparecer em D3N.
    """
    preferred_keys = ["D3N", "D3C", "D2N", "D2C", "D4N", "D4C"]

    for key in preferred_keys:
        candidate = parse_int(row.get(key))
        if candidate is not None and 1900 <= candidate <= 2100:
            return candidate

    for key, value in row.items():
        if key.startswith("D") and key[-1] in {"C", "N"}:
            candidate = parse_int(value)
            if candidate is not None and 1900 <= candidate <= 2100:
                return candidate

    return None


def get_populacao_df(municipios_df: pd.DataFrame) -> pd.DataFrame:
    """
    Baixa a população estimada municipal mais recente pela tabela 6579 do SIDRA.

    Retorna um DataFrame simples para os trainees decidirem como integrar
    esse dado ao modelo relacional.
    """
    data = get_json(SIDRA_POPULACAO_URL)

    if not data or len(data) <= 1:
        raise RuntimeError("A API do SIDRA não retornou dados suficientes.")

    valid_municipio_ids = set(municipios_df["id_municipio"].dropna().astype(int))

    rows = []

    # A primeira linha normalmente é o cabeçalho.
    for item in data[1:]:
        municipio_id = find_municipio_id(item, valid_municipio_ids)
        ano = find_ano(item)
        valor = parse_float(item.get("V"))

        if municipio_id is None or ano is None or valor is None:
            continue

        rows.append(
            {
                "id_municipio": municipio_id,
                "ano": ano,
                "indicador": "populacao_residente_estimada",
                "valor": valor,
                "unidade": "pessoas",
                "fonte": "IBGE/SIDRA tabela 6579",
            }
        )

    return pd.DataFrame(rows)


def build_dataframes() -> dict[str, pd.DataFrame]:
    """
    Cria todos os DataFrames usados no exercício.

    Alguns DataFrames têm informações repetidas de propósito.
    Isso permite discutir normalização na aula.
    """
    regioes_df = get_regioes_df()
    estados_df = get_estados_df()
    municipios_df = get_municipios_df()
    populacao_df = get_populacao_df(municipios_df)

    municipios_com_populacao_df = municipios_df.merge(
        populacao_df,
        on="id_municipio",
        how="left",
    )

    return {
        "regioes": regioes_df,
        "estados": estados_df,
        "municipios": municipios_df,
        "populacao_municipal": populacao_df,
        "municipios_com_populacao": municipios_com_populacao_df,
    }


def save_dataframes(dataframes: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """Salva os DataFrames em CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, df in dataframes.items():
        path = output_dir / f"{name}.csv"
        df.to_csv(path, index=False, encoding="utf-8")
        print(
            f"CSV gerado: {path} | "
            f"linhas: {len(df)} | "
            f"colunas: {len(df.columns)}"
        )


def show_summary(dataframes: dict[str, pd.DataFrame]) -> None:
    """Mostra um resumo dos DataFrames gerados."""
    print("\nResumo dos DataFrames gerados:\n")

    for name, df in dataframes.items():
        print(f"--- {name} ---")
        print(f"linhas: {len(df)}")
        print(f"colunas: {list(df.columns)}")
        print(df.head(3))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Baixa dados reais do IBGE e gera DataFrames/CSVs "
            "para o módulo de Banco de Dados."
        )
    )

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=(
            "Pasta onde os CSVs serão salvos. "
            "Padrão: data/raw dentro da pasta banco_de_dados."
        ),
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Não salva CSVs, apenas mostra o resumo dos DataFrames.",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    print("\nPasta do script:")
    print(SCRIPT_DIR)

    print("\nPasta de saída dos CSVs:")
    print(output_dir)

    dataframes = build_dataframes()
    show_summary(dataframes)

    if not args.no_save:
        save_dataframes(dataframes, output_dir)


if __name__ == "__main__":
    main()