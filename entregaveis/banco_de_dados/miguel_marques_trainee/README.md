# Entrega Banco de Dados 1 - miguel_marques

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado utilizando SQLite, com criação de tabelas, chaves primárias, chaves estrangeiras e consultas SQL.

## Arquivos da entrega

- `database.db`: banco SQLite com os dados brutos e tabelas normalizadas.
- `schema.sql`: criação das tabelas finais do modelo relacional.
- `carga.sql`: carregamento dos dados das tabelas `raw_` para as tabelas finais.
- `queries.sql`: consultas SQL de exploração e validação do banco.
- `analytics.sql`: consultas analíticas sobre os dados populacionais.
- `modelo_logico.png`: modelo lógico criado no DBeaver.

## Dados brutos

As tabelas com prefixo `raw_` foram carregadas a partir dos CSVs gerados com dados reais do IBGE.

A partir dessas tabelas, foi criado um modelo normalizado utilizando as tabelas `regioes`, `estados`, `municipios`, `indicadores` e `fato_indicador_municipal`, mantendo os relacionamentos através de chaves primárias e chaves estrangeiras.

## Modelo criado

O banco foi estruturado com os seguintes relacionamentos:

- Regiões possuem estados.
- Estados possuem municípios.
- Municípios possuem indicadores populacionais.
- A tabela fato armazena os valores dos indicadores por município e ano.
  