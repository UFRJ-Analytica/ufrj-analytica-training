# Entrega Banco de Dados I - Pedro Tonelli

## Objetivo

Transformar as tabelas brutas `raw_` (dados reais do IBGE) em um modelo
relacional **normalizado** em SQLite e responder perguntas de negocio com SQL.

## Fonte dos dados

- **IBGE / Localidades** - regioes, estados (UFs) e municipios.
- **IBGE / SIDRA tabela 6579** (variavel 9324) - populacao residente
  estimada por municipio (periodo mais recente disponivel: **2025**).

Os dados sao baixados por `get_data_ibge.py` e carregados como tabelas
`raw_` por `load_raw_to_sqlite.py`. Um municipio sem microrregiao cadastrada
na API (Boa Esperanca do Norte/MT) e ignorado pelo script de coleta,
resultando em **5.570 municipios**.

## Modelo relacional

Modelo normalizado (3FN) com uma hierarquia geografica
`regiao -> estado -> municipio` e uma tabela fato de indicadores, separada
de uma tabela de dimensao `indicadores`.

| Tabela | PK | FKs | Descricao |
|---|---|---|---|
| `regioes` | `id_regiao` | - | 5 grandes regioes |
| `estados` | `id_uf` | `id_regiao -> regioes` | 27 UFs |
| `municipios` | `id_municipio` | `id_uf -> estados` | 5.570 municipios |
| `indicadores` | `id_indicador` (auto) | - | metadados do indicador (codigo, unidade, fonte) |
| `fato_indicador_municipal` | (`id_municipio`, `id_indicador`, `ano`) | `id_municipio -> municipios`, `id_indicador -> indicadores` | valor do indicador por municipio/ano |

**Por que normalizar assim:** cada informacao (nome da regiao, nome da UF)
fica armazenada uma unica vez, na sua tabela propria, e e referenciada por
chave estrangeira. Isso elimina a redundancia presente na tabela bruta
`raw_municipios_com_populacao` (onde nome de regiao/UF se repetia em cada
linha de municipio) e garante integridade referencial: nao e possivel
cadastrar um municipio de uma UF inexistente, nem um valor de indicador para
um municipio inexistente.

A tabela fato (`fato_indicador_municipal`) foi separada da dimensao
`indicadores` em vez de usar uma unica tabela `populacao_municipal` com o
texto do indicador repetido em cada linha (como estava em `raw_`). Hoje so
existe um indicador (`populacao_residente_estimada`), mas essa modelagem
permite adicionar outros indicadores do IBGE no futuro (PIB per capita, IDH,
area territorial etc.) sem alterar o esquema, apenas inserindo uma nova
linha em `indicadores` e novas linhas na tabela fato.

## Como reproduzir

Pre-requisitos: Python com `pandas`, `SQLAlchemy` e `requests`
(ver `requirements.txt` na pasta `banco_de_dados`). Rodar a partir de
`entregaveis/banco_de_dados/`:

```bash
# 1. baixar os CSVs reais do IBGE -> data/raw/  (nao versionado)
python get_data_ibge.py

# 2. criar a pasta individual e o database.db com as tabelas raw_
python load_raw_to_sqlite.py --name "Pedro Tonelli"

# 3. aplicar o modelo normalizado e a carga (via DBeaver ou sqlite3)
#    conectar em pedro_tonelli_trainee/database.db e executar, nesta ordem:
#      schema.sql   -> cria as tabelas finais (PKs + FKs)
#      carga.sql    -> popula as finais a partir das raw_
```

> `schema.sql` usa `DROP TABLE IF EXISTS` apenas nas tabelas **finais**; as
> `raw_` nunca sao apagadas. Ative `PRAGMA foreign_keys = ON;` na conexao
> para que as FKs sejam checadas.

## Principais consultas

**`queries.sql`** - exploracao e validacao do banco normalizado: listagem de
regioes/estados/municipios, filtros por regiao/UF, join municipio-estado-
regiao, contagem de municipios por estado/regiao, populacao total por
estado, Top 10 estados em quantidade de municipios, e uma tabela de teste
(`teste_operacoes`) com um `INSERT`, um `UPDATE` e um `DELETE` registrados
em sequencia.

**`analytics.sql`** - consultas analiticas: ranking dos municipios mais
populosos (nacional e por UF), populacao total e percentual por regiao,
populacao media por estado, municipios acima da media nacional,
classificacao dos municipios por porte (pequeno/medio/grande) nacional e
por regiao, e uma analise de concentracao populacional (percentual da
populacao de cada estado que esta nos 3 municipios mais populosos daquele
estado, usando `ROW_NUMBER() OVER (PARTITION BY ...)`).

## Validacao

Todas as consultas de `schema.sql`, `carga.sql`, `queries.sql` e
`analytics.sql` foram executadas contra o `database.db` e rodaram sem erro.
`PRAGMA foreign_key_check` nao encontrou nenhuma violacao de chave
estrangeira apos a carga.
