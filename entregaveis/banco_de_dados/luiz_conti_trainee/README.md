# Entrega Banco de Dados 1 - Luiz Conti

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

## Criação do schema e normalização

Para a criação do schema, realizei a normalização do database bruto para a 3FN através da divisão do database em tabelas "atômicas". A normalização
resultou em 4 tabelas (estados, municipios, indicadores, fato_indicador_municipal e regioes). Por exemplo, antes a coluna nome_regiao estava na tabela municipios, mesmo sendo um atributo de região. Agora, só é possivel acessar essa coluna através da tabela regioes (utilizando o id da região como referência). 

A tabela de municípios com população "sumiu" com a normalização, pois ela continha informações referentes a tabelas já existentes (municipios, indicadores e fato_indicador_municipal).

Na tabela fato_indicador_municipal, usei como chave primária o trio de ano, id_municipio e id_indicador, supondo que essa estimativa de população muda de ano em ano (apesar de no database ter apenas 2025) e que o database possa ter mais de um indicador.

## Carga no database

Para realizar a carga, utilizei queries com o comando INSERT, buscando puxar apenas as colunas referentes à normalização realizada na etapa anterior. Também puxei apenas linhas únicas.
Basicamente as cincos queries de carga possuem a mesma estrutura, com execeção da carga no fato_indicador_municipal, onde precisei fazer um join com a tabela indicadores.
