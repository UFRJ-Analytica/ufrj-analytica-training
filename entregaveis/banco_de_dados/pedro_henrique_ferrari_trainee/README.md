# Entrega Banco de Dados 1 - Pedro Henrique Ferrari

## Objetivo

Organizar os dados brutos do IBGE em um banco relacional normalizado e realizar consultas em SQL.

## Modelo

O banco possui as tabelas:

- `regioes`
- `estados`
- `municipios`
- `populacao_municipal`

A relação entre elas é:

`regioes → estados → municipios → populacao_municipal`

## Arquivos

- `database.db`: banco SQLite
- `schema.sql`: criação das tabelas
- `carga.sql`: carga dos dados
- `queries.sql`: consultas obrigatórias
- `analytics.sql`: consultas analíticas
- `modelo_logico.png`: modelo lógico do banco

## Dados

As tabelas com prefixo `raw_` foram preservadas no banco. As consultas utilizam principalmente as tabelas normalizadas.
