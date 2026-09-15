
 database.db:banco de dados do SQLite.
 schema.sql:criação das tabelas finais.
 carga.sql:carregamento dos dados nas tabelas finais.
 queries.sql:consultas SQL.
 analytics.sql: consultas para análise dos dados.
 modelo_logico.png: modelo lógico do banco feito no DBeaver.


regioes: informações sobre as regiões.
estados: informações sobre os estados e suas regiões.
municipios: informações sobre os municípios e seus estados.
populacao_municipal: dados de população dos municípios.

Os relacionamentos pedidos são:

estados.id_regiao aponta  regioes.id_regiao
municipios.id_uf aponta para estados.id_uf
populacao_municipal.id_municipio aponta para municipios.id_municipio



As tabelas foram separadas para evitar repetir informações. Por exemplo,o nome de uma região não precisa ficar repetido em todos os estados.

A tabela populacao_municipal possui um id próprio como chave primária e usa id_municipio para se relacionar com a tabela municipios.

