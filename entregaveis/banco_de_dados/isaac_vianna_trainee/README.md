# Entrega Banco de Dados I - Isaac Vianna

## Objetivo

Transformar as tabelas brutas `raw_` (dados reais do IBGE) em um modelo relacional
**normalizado** em SQLite e responder perguntas de negócio com SQL.

## Fonte dos dados

- **IBGE / Localidades** — regiões, estados (UFs) e municípios.
- **IBGE / SIDRA tabela 6579** (variável 9324) — população residente estimada por
  município (período mais recente disponível: **2025**).

Os dados são baixados por `get_data_ibge.py` e carregados como tabelas `raw_` por
`load_raw_to_sqlite.py`. Municípios sem microrregião cadastrada na API são
ignorados pelo script de coleta (1 caso: Boa Esperança do Norte/MT), resultando em
**5.570 municípios**.

## Modelo relacional

Modelo normalizado (3FN) com uma hierarquia geográfica `regiões → estados →
municípios` e uma tabela de fatos de população. As colunas mantêm os nomes
originais dos CSVs do IBGE (`id_uf`, `valor`, `indicador`, `unidade`, `fonte`).

| Tabela | PK | FKs | Descrição |
|---|---|---|---|
| `regioes` | `id_regiao` | — | 5 grandes regiões do país |
| `estados` | `id_uf` | `id_regiao → regioes` | 27 UFs |
| `municipios` | `id_municipio` | `id_uf → estados` | 5.570 municípios |
| `populacao_municipal` | (`id_municipio`, `ano`, `indicador`) | `id_municipio → municipios` | população estimada por município/ano/indicador |

**Por que normalizar assim:** nas tabelas `raw_`, o nome da região e o nome da UF
se repetem em toda linha de município (`raw_municipios_com_populacao` chega a
repetir 6 colunas geográficas por linha). Extraindo `regioes`, `estados` e
`municipios` em tabelas próprias e referenciando-as por chave estrangeira, cada
informação passa a existir uma única vez, e o banco garante integridade
referencial: não é possível cadastrar um estado com região inexistente, nem um
município com UF inexistente. A população fica em uma tabela de fatos separada,
com chave primária composta (`id_municipio`, `ano`, `indicador`) — não faz sentido
existir duas medições do mesmo indicador, no mesmo município, no mesmo ano, e essa
composição evita duplicidade sem precisar de um id artificial. Optei por não criar
uma tabela `indicadores` separada porque hoje só existe um único indicador
(população residente estimada); criar uma dimensão própria para um valor fixo
seria complexidade sem benefício real no momento — o modelo já está preparado para
receber novos indicadores simplesmente inserindo novas linhas em
`populacao_municipal` com outro valor de `indicador`.

## Como reproduzir

Pré-requisitos: Python com `pandas`, `SQLAlchemy` e `requests` (ver
`requirements.txt` na pasta `banco_de_dados`). Rodar a partir de
`entregaveis/banco_de_dados/`:

```bash
# 1. baixar os CSVs reais do IBGE -> data/raw/ (não versionado)
python get_data_ibge.py

# 2. criar a pasta individual e o database.db com as tabelas raw_
python load_raw_to_sqlite.py --name "Isaac Vianna"

# 3. aplicar o modelo normalizado e a carga (via DBeaver ou sqlite3)
#    conectar em isaac_vianna_trainee/database.db e executar, nesta ordem:
#      schema.sql   -> cria as tabelas finais (PKs + FKs)
#      carga.sql    -> popula as finais a partir das raw_
#      queries.sql  -> consultas obrigatórias
#      analytics.sql -> consultas analíticas + view
```

> `schema.sql` usa `DROP TABLE IF EXISTS` apenas nas tabelas **finais**; as `raw_`
> nunca são apagadas. Ative `PRAGMA foreign_keys = ON;` na conexão para que as FKs
> sejam checadas (já incluído no início de `schema.sql` e `carga.sql`).

## Arquivos da entrega

- `database.db` — banco SQLite com as tabelas `raw_` + o modelo normalizado.
- `schema.sql` — criação das tabelas normalizadas (PKs e FKs).
- `carga.sql` — carga das tabelas finais a partir das `raw_`.
- `queries.sql` — 10 consultas obrigatórias (SELECT, JOIN, GROUP BY, INSERT, UPDATE, DELETE).
- `analytics.sql` — 6 consultas analíticas (rankings, agregações, subquery, CASE, view).
- `modelo_logico.png` — diagrama do modelo lógico (tabelas, PKs, FKs e relacionamentos).

## Resumo das consultas

### `queries.sql` (10 consultas)

Cada consulta é precedida de um comentário `-- N. <pergunta>` com a pergunta que
ela responde:

1. Quais regiões existem na base?
2. Quais estados pertencem a uma região escolhida? (Sudeste)
3. Quais municípios pertencem a uma UF escolhida? (RJ)
4. Qual é o estado e a região de cada município?
5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
6. Quantos municípios existem por estado?
7. Quantos municípios existem por região?
8. Qual é a população total estimada por estado?
9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
10. Tabela `teste_operacoes` com uma inserção, uma alteração e uma remoção de
    registro, sem alterar as tabelas finais do modelo.

### `analytics.sql` (6 consultas)

Mesmo padrão de comentário, uma pergunta analítica por consulta:

1. Quais são os municípios mais populosos da base? (`RANK() OVER`)
2. Qual é a população total estimada por região?
3. Qual é a população média dos municípios por estado?
4. Quais municípios possuem população acima da média nacional dos municípios? (subconsulta)
5. Quantos municípios pequenos, médios e grandes existem por região? (`CASE`)
6. Qual região concentra a maior população estimada? (`VIEW vw_populacao_por_regiao`
   com participação percentual de cada região)

**Alguns achados:** o Sudeste concentra ~41,6% da população nacional, seguido pelo
Nordeste (~26,8%); São Paulo é o município mais populoso do país (~11,9 milhões),
seguido do Rio de Janeiro (~6,7 milhões) e de Brasília (~3,0 milhões).
