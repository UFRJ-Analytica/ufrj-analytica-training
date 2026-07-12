# Entrega Banco de Dados 1 - gabriel basto

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

Separei a tabela indicadores da tabela fato_indicador_municipal porque na raw_populacao_municipal cada linha repete o texto do nome, do indicador, a unidade e a fonte. Isso é redundância. Ao criar uma tabela indicadores e referenciar por id_indicador, o modelo elimina a repetição e fica apto a receber novos indicadores no futuro.

O fato_indicador_municipal possui chave primaria composta porque (id_municipio, id_indicador, ano) é o que identifica unicamente uma medição, não é possivel ter duas populaçoes estimadas para o mesmo municipio no mesmo ano. usar uma primary key composta em vez de um id autoincremento evita duplicidade de dados.
