# Entrega Banco de Dados 1 - Camila Caleones

## Objetivo

Transformar as tabelas brutas `raw_` (dados reais do IBGE) em um modelo relacional
**normalizado** em SQLite e responder perguntas de negócio com SQL.

## Fonte dos dados

- **IBGE / Localidades** — regiões, estados (UFs) e municípios.
- **IBGE / SIDRA tabela 6579** (variável 9324) — população residente estimada por
  município (período mais recente disponível: **2025**).

Os dados são baixados por `get_data_ibge.py` e carregados como tabelas `raw_` por
`load_raw_to_sqlite.py`. Um município sem microrregião na API é ignorado pelo script,
resultando em **5.570 municípios**.

## Modelo relacional

Modelo normalizado (3FN) com uma hierarquia geográfica `região → estado → município`
e uma tabela de fatos de população. As colunas seguem os nomes oficiais dos CSVs
do IBGE (`id_uf`, `valor`, `indicador`, `unidade`, `fonte`).

| Tabela | PK | FKs | Descrição |
|---|---|---|---|
| `regioes` | `id_regiao` | — | 5 grandes regiões |
| `estados` | `id_uf` | `id_regiao → regioes` | 27 UFs |
| `municipios` | `id_municipio` | `id_uf → estados` | 5.570 municípios |
| `populacao_municipal` | (`id_municipio`, `ano`, `indicador`) | `id_municipio → municipios` | população estimada por município/ano |

**Por que normalizar assim:** cada informação (nome da região, nome da UF) fica
armazenada uma única vez, na sua tabela própria, e é referenciada por chave
estrangeira. Isso elimina a redundância presente nas tabelas `raw_` (onde nome de
região/UF se repetia em cada linha de município) e garante integridade referencial:
não é possível cadastrar um município de uma UF inexistente, nem população de um
município inexistente. A população fica numa tabela de fatos separada, com PK
composta (`id_municipio`, `ano`, `indicador`), permitindo evoluir para outros anos
ou indicadores sem alterar o esquema.

## Como reproduzir

Pré-requisitos: Python com `pandas`, `SQLAlchemy` e `requests` (ver `requirements.txt`
na pasta `banco_de_dados`). Rodar a partir de `entregaveis/banco_de_dados/`:

```bash
# 1. baixar os CSVs reais do IBGE -> data/raw/  (não versionado)
python get_data_ibge.py

# 2. criar a pasta individual e o database.db com as tabelas raw_
python load_raw_to_sqlite.py --name "Camila Caleones"

# 3. aplicar o modelo normalizado e a carga (via DBeaver ou sqlite3)
#    conectar em camila_caleones/database.db e executar, nesta ordem:
#      schema.sql   -> cria as tabelas finais (PKs + FKs)
#      carga.sql    -> popula as finais a partir das raw_
```

> `schema.sql` usa `DROP TABLE IF EXISTS` apenas nas tabelas **finais**; as `raw_`
> nunca são apagadas. Ative `PRAGMA foreign_keys = ON;` na conexão para que as FKs
> sejam checadas.

## Arquivos da entrega

- `database.db` — banco SQLite com as tabelas `raw_` + o modelo normalizado.
- `schema.sql` — criação das tabelas normalizadas (PKs e FKs).
- `carga.sql` — carga das tabelas finais a partir das `raw_`.
- `queries.sql` — 10 consultas obrigatórias.
- `analytics.sql` — 6 consultas analíticas.
- `modelo_logico.png` — modelo lógico exportado do DBeaver.

## Resumo das consultas

### `queries.sql` (10 obrigatórias)

Cobre `SELECT`, `JOIN`, `GROUP BY`, `INSERT`, `UPDATE` e `DELETE`:

1. Regiões existentes na base.
2. Estados de uma região escolhida (ex.: Sudeste).
3. Municípios de uma UF escolhida (ex.: RJ).
4. Estado e região de cada município.
5. População estimada dos municípios (município, UF, região, ano, valor).
6. Quantidade de municípios por estado.
7. Quantidade de municípios por região.
8. População total estimada por estado.
9. Top 10 estados por quantidade de municípios.
10. Tabela de teste demonstrando `INSERT`, `UPDATE` e `DELETE`.

### `analytics.sql` (6 analíticas)

1. Ranking dos 10 municípios mais populosos.
2. População total por região.
3. População média dos municípios por estado.
4. Municípios acima da média nacional (subconsulta).
5. Classificação por porte (`CASE`: pequeno / médio / grande) e contagem por região.
6. Concentração: participação (%) de cada região na população nacional, via
   `VIEW vw_populacao_por_regiao`.

**Alguns achados:** o Sudeste concentra ~41,6% da população nacional; o Nordeste tem
o maior número de municípios (1.794); e a grande maioria dos municípios (4.888 de
5.570) tem menos de 50 mil habitantes.
