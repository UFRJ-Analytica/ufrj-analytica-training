# Entrega Banco de Dados 1 - Marcelo Borges

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

## Justificativas da Modelagem
A tabela regiao permaneceu inalterada em relação a tabela regioes.csv.
A tabela estado foi normalizada com atributos relevantes a essa entidade - id_uf, nome_uf, sigla_uf - e com a foreign key para a tabela regiao.
A tabela municipio foi normalizada com os atributos id_municipio e nome_municipio e uma foreign key para o estado a que cada municipio pertence.
A tabela populacao_municipal foi normalizada a partir de raw_municipios_com_populacao, com os atributos id_municipio, id_censo e valor.
A tabela censo foi normalizada a partir de raw_municipios_com_populacao com as informações do censo - id_censo, ano, indicador, unidade e fonte.
