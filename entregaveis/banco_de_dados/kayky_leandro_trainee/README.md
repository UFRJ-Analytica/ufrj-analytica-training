# Entrega Banco de Dados 1 - kayky leandro

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado.

## Arquivos da entrega

- `database.db`: banco SQLite com dados brutos e tabelas criadas.
- `normalizacao.sql`: criação e população das tabelas normalizadas.
- `queries.sql`: consultas SQL obrigatórias.
- `analytics.sql`: consultas analíticas ou proposta de camada analítica.
- `modelo_logico.png`: imagem do modelo lógico feito no DBeaver.

## Estrutura do banco

O banco foi modelado com as seguintes tabelas:

- regioes
- estados
- municipios
- indicadores
- fato_indicador_municipal

As tabelas brutas (`raw_`) foram preservadas e utilizadas como origem para a carga das tabelas normalizadas.

## Arquivos

- schema.sql → criação das tabelas
- carga.sql → carga dos dados
- queries.sql → consultas obrigatórias
- analytics.sql → consultas analíticas
- modelo_logico.png → diagrama do banco

## Tecnologias utilizadas

- SQLite
- DBeaver
- SQL

## Como executar

1. Execute `schema.sql`.
2. Execute `carga.sql`.
3. Execute `queries.sql`.
4. Execute `analytics.sql`.

Todos os scripts podem ser executados no DBeaver utilizando o arquivo `database.db`.