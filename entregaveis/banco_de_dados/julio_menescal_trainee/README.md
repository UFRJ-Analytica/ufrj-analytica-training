# Entrega Banco de Dados 1 - Julio Menescal

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado e realizar consultas e análises sobre os dados do IBGE.

## Arquivos da entrega

- `database.db`: banco SQLite com os dados brutos e as tabelas finais normalizadas.
- `schema.sql`: criação das tabelas finais normalizadas.
- `carga.sql`: população das tabelas finais a partir das tabelas brutas.
- `queries.sql`: consultas SQL de exploração e validação do banco.
- `analytics.sql`: consultas analíticas sobre os dados populacionais.
- `modelo_logico.png`: imagem do modelo lógico criado no DBeaver.

## Dados brutos

As tabelas com prefixo `raw_` foram carregadas automaticamente a partir dos CSVs gerados com dados reais do IBGE.

Essas tabelas foram preservadas no banco e utilizadas como fonte para a criação e população das tabelas finais normalizadas.

## Modelo relacional

O modelo final foi organizado nas tabelas:

- `regioes`;
- `estados`;
- `municipios`;
- `populacao_municipal`.

Os relacionamentos seguem a estrutura:

`regioes → estados → municipios → populacao_municipal`

Foram utilizadas chaves primárias e chaves estrangeiras para representar os relacionamentos entre as entidades e reduzir a repetição de informações presente nas tabelas brutas.

## Consultas

O arquivo `queries.sql` contém consultas para exploração e validação do banco, utilizando filtros, ordenações, relacionamentos entre tabelas, agrupamentos e funções de agregação.

Também foi criada uma tabela de teste para a realização de operações de inserção, alteração e remoção de registros.

## Análises

O arquivo `analytics.sql` contém análises sobre:

- os municípios mais populosos da base;
- a população total estimada por região;
- a população média dos municípios por estado;
- os municípios com população acima da média nacional;
- a quantidade de municípios pequenos, médios e grandes;
- a distribuição dos municípios pequenos, médios e grandes por região.

Para a classificação por porte populacional, foram considerados:

- pequenos: menos de 50.000 habitantes;
- médios: entre 50.000 e 499.999 habitantes;
- grandes: 500.000 habitantes ou mais.