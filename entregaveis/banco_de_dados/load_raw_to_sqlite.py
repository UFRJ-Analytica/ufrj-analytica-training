"""
load_raw_to_sqlite.py

Carrega os CSVs gerados pelo script do IBGE para um banco SQLite individual
de cada trainee.

Este script NÃO cria o modelo normalizado final.
Ele apenas cria/carrega tabelas brutas com prefixo raw_ dentro do database.db
da pasta individual do trainee.

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

Após rodar, será criado:

ufrj-analytica-training/
  entregaveis/
    banco_de_dados/
      nome_sobrenome_trainee/
        database.db
        README.md
        normalizacao.sql
        queries.sql
        analytics.sql

Uso:
    1. Altere a variável TRAINEE_NAME abaixo.
    2. Rode:
        python load_raw_to_sqlite.py

Uso alternativo:
    python load_raw_to_sqlite.py --name "Lucas Passos"
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import unicodedata
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


# =========================================================
# ALTERE AQUI
# =========================================================
# Troque pelo seu nome.
# Exemplo:
# TRAINEE_NAME = "Lucas Passos"
TRAINEE_NAME = "Julia Vilela"


# =========================================================
# CONFIGURAÇÕES DO PROJETO
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = SCRIPT_DIR / "data" / "raw"

CSV_TO_TABLE = {
    "regioes.csv": "raw_regioes",
    "estados.csv": "raw_estados",
    "municipios.csv": "raw_municipios",
    "populacao_municipal.csv": "raw_populacao_municipal",
    "municipios_com_populacao.csv": "raw_municipios_com_populacao",
}


def slugify_name(name: str) -> str:
    """
    Converte o nome do trainee para um nome seguro de pasta.

    Exemplos:
        "Lucas Passos" -> "lucas_passos"
        "João da Silva" -> "joao_da_silva"
    """
    name = name.strip().lower()

    if not name:
        raise ValueError("O nome do trainee não pode estar vazio.")

    normalized = unicodedata.normalize("NFKD", name)
    without_accents = normalized.encode("ascii", "ignore").decode("ascii")

    slug = re.sub(r"[^a-z0-9]+", "_", without_accents)
    slug = re.sub(r"_+", "_", slug).strip("_")

    if not slug:
        raise ValueError("O nome informado não gerou um nome de pasta válido.")

    return slug


def validate_trainee_name(name: str) -> None:
    """Garante que o trainee alterou o nome padrão."""
    invalid_names = {
        "COLOQUE_SEU_NOME_AQUI",
        "troque_pelo_seu_nome",
        "seu_nome",
        "",
    }

    if name.strip() in invalid_names:
        raise ValueError(
            "\nVocê ainda não informou seu nome.\n\n"
            "Abra o arquivo load_raw_to_sqlite.py e altere a linha:\n\n"
            '    TRAINEE_NAME = "COLOQUE_SEU_NOME_AQUI"\n\n'
            "Exemplo:\n\n"
            '    TRAINEE_NAME = "Lucas Passos"\n\n'
            "Ou rode pelo terminal assim:\n\n"
            '    python load_raw_to_sqlite.py --name "Lucas Passos"\n'
        )


def validate_input_files(input_dir: Path) -> None:
    """Verifica se a pasta data/raw e os CSVs esperados existem."""
    if not input_dir.exists():
        raise FileNotFoundError(
            f"\nPasta de dados não encontrada: {input_dir}\n\n"
            "Rode primeiro o script get_ibge_dataframes.py para gerar os CSVs.\n"
        )

    missing_files = []

    for csv_file in CSV_TO_TABLE:
        csv_path = input_dir / csv_file
        if not csv_path.exists():
            missing_files.append(csv_file)

    if missing_files:
        missing_text = "\n".join(f"- {file}" for file in missing_files)
        raise FileNotFoundError(
            "\nOs seguintes arquivos CSV não foram encontrados:\n"
            f"{missing_text}\n\n"
            f"Pasta verificada: {input_dir}\n\n"
            "Rode primeiro o script get_ibge_dataframes.py.\n"
        )


def create_trainee_folder(trainee_name: str) -> Path:
    """
    Cria a pasta individual do trainee dentro da pasta banco_de_dados.

    Exemplo:
        banco_de_dados/lucas_passos_trainee
    """
    slug = slugify_name(trainee_name)
    trainee_dir = SCRIPT_DIR / f"{slug}_trainee"
    trainee_dir.mkdir(parents=True, exist_ok=True)
    return trainee_dir


def load_csv_to_sqlite(csv_path: Path, table_name: str, engine) -> None:
    """
    Lê um CSV e grava como tabela bruta no SQLite.

    if_exists='replace' substitui apenas a tabela raw_ correspondente.
    Isso permite rodar o script novamente sem apagar tabelas normalizadas
    que o trainee tenha criado, desde que elas não tenham prefixo raw_.
    """
    print(f"Carregando {csv_path.name} → {table_name}")

    df = pd.read_csv(csv_path)

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
    )

    print(f"  Linhas: {len(df)} | Colunas: {len(df.columns)}")


def create_metadata_table(engine, trainee_name: str, db_path: Path, input_dir: Path) -> None:
    """
    Cria uma tabela simples de metadados da carga.
    Ajuda na correção e no rastreio do processo.
    """
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS metadata_carga (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                );
                """
            )
        )

        conn.execute(text("DELETE FROM metadata_carga;"))

        metadata = {
            "trainee_name": trainee_name,
            "database_path": str(db_path),
            "input_dir": str(input_dir),
            "descricao": (
                "Tabelas raw_ carregadas a partir dos CSVs gerados "
                "com dados reais do IBGE."
            ),
        }

        for chave, valor in metadata.items():
            conn.execute(
                text(
                    """
                    INSERT INTO metadata_carga (chave, valor)
                    VALUES (:chave, :valor);
                    """
                ),
                {"chave": chave, "valor": valor},
            )


def create_template_files_if_missing(trainee_dir: Path, trainee_name: str) -> None:
    """
    Cria arquivos de entrega vazios/modelo, sem sobrescrever caso já existam.
    """
    files = {
        "README.md": f"""# Entrega Banco de Dados 1 - {trainee_name}

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado.

## Arquivos da entrega

- `database.db`: banco SQLite com dados brutos e tabelas criadas.
- `normalizacao.sql`: criação e população das tabelas normalizadas.
- `queries.sql`: consultas SQL obrigatórias.
- `analytics.sql`: consultas analíticas ou proposta de camada analítica.
- `modelo_logico.png`: imagem do modelo lógico feito no DBeaver.

## Dados brutos

As tabelas com prefixo `raw_` foram carregadas automaticamente a partir dos CSVs gerados com dados reais do IBGE.

A partir delas, crie o modelo final normalizado.
""",
        "schema.sql": """-- schema.sql
-- Defina aqui a estrutura do banco de dados normalizado.
""", 
        "carga.sql": """-- carga.sql
-- Defina aqui as instruções para carregar os dados das tabelas brutas para as tabelas normalizadas.
""", 
        "queries.sql": """-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.
""",
        "analytics.sql": """-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.
""",
    }

    for filename, content in files.items():
        path = trainee_dir / filename

        if not path.exists():
            path.write_text(content, encoding="utf-8")


def print_table_counts(db_path: Path) -> None:
    """Mostra as tabelas existentes no database.db e suas contagens."""
    conn = sqlite3.connect(db_path)

    try:
        tables = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
            """
        ).fetchall()

        print("\nTabelas encontradas no database.db:\n")

        for (table_name,) in tables:
            count = conn.execute(f'SELECT COUNT(*) FROM "{table_name}";').fetchone()[0]
            print(f"- {table_name}: {count} linhas")

    finally:
        conn.close()


def run(trainee_name: str, input_dir: Path) -> None:
    """Executa a carga bruta no database.db individual do trainee."""
    validate_trainee_name(trainee_name)
    validate_input_files(input_dir)

    trainee_dir = create_trainee_folder(trainee_name)
    db_path = trainee_dir / "database.db"

    engine = create_engine(f"sqlite:///{db_path}")

    print("\nIniciando carga bruta no SQLite")
    print(f"Trainee: {trainee_name}")
    print(f"Pasta da entrega: {trainee_dir}")
    print(f"Banco SQLite: {db_path}")
    print(f"Pasta dos CSVs: {input_dir}\n")

    for csv_file, table_name in CSV_TO_TABLE.items():
        csv_path = input_dir / csv_file
        load_csv_to_sqlite(csv_path, table_name, engine)

    create_metadata_table(
        engine=engine,
        trainee_name=trainee_name,
        db_path=db_path,
        input_dir=input_dir,
    )

    create_template_files_if_missing(
        trainee_dir=trainee_dir,
        trainee_name=trainee_name,
    )

    print_table_counts(db_path)

    print("\nCarga concluída com sucesso.")
    print("\nAbra este arquivo no DBeaver:")
    print(db_path)

    print("\nPróximo passo:")
    print("1. Abrir o database.db no DBeaver.")
    print("2. Analisar as tabelas raw_.")
    print("3. Preencher o normalizacao.sql.")
    print("4. Criar o modelo lógico e salvar como modelo_logico.png.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cria a pasta individual do trainee e carrega os CSVs brutos "
            "em um database.db SQLite."
        )
    )

    parser.add_argument(
        "--name",
        default=TRAINEE_NAME,
        help='Nome do trainee. Exemplo: --name "Lucas Passos"',
    )

    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR),
        help=(
            "Pasta dos CSVs. "
            "Padrão: data/raw dentro da pasta banco_de_dados."
        ),
    )

    args = parser.parse_args()

    run(
        trainee_name=args.name,
        input_dir=Path(args.input_dir),
    )


if __name__ == "__main__":
    main()