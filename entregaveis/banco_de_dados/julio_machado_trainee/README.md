# Entrega Banco de Dados 1 - julio_machado

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado.

## Arquivos da entrega

- `database.db`: banco SQLite com dados brutos e tabelas criadas.
- `schema.sql`: criação das tabelas normalizadas.
- `carga.sql`: população das tabelas normalizadas.
- `queries.sql`: consultas SQL obrigatórias.
- `analytics.sql`: consultas analíticas ou proposta de camada analítica.
- `modelo_logico.png`: imagem do modelo lógico feito no DBeaver.

## Dados brutos

As tabelas com prefixo `raw_` foram carregadas automaticamente a partir dos CSVs gerados com dados reais do IBGE.

A partir delas, crie o modelo final normalizado.

## Modelo criado
O modelo que criei é um relacionamento regiões -> Estados -> Municípios -> Recenseamento(tabela relacional para relacionamento n pra n) -> Censos, em Censos ficam o ano e a fonte do censo e na tabela recenseamento fica a população e a unidade de medida, junto com os ids necessários para realizar as junções entre municípios e os censos. Dei a tabela esse nome pois um município sofre recenseamento varias vezes e o IBGE recenseia diversos municípios.

## Lógica geral das consultas
Eu pensei nas consultas como a construção de uma tabela que resolvesse as minhas perguntas, portanto usei bastante o inner join. Sempre tentei incluir o id_censo nas minhas consultas, para que elas não quebrassem caso um novo censo fosse adicionado.