-- carga.sql
-- População das tabelas normalizadas a partir das tabelas raw_.

PRAGMA foreign_keys = ON;

DELETE FROM populacao_municipal;
DELETE FROM municipios;
DELETE FROM estados;
DELETE FROM regioes;

INSERT INTO regioes (id_regiao, nome_regiao, sigla_regiao)
SELECT DISTINCT id_regiao, nome_regiao, sigla_regiao
FROM raw_regioes;

INSERT INTO estados (id_uf, nome_uf, sigla_uf, id_regiao)
SELECT DISTINCT id_uf, nome_uf, sigla_uf, id_regiao
FROM raw_estados;

INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios;

INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
SELECT DISTINCT id_municipio, ano, indicador, valor, unidade, fonte
FROM raw_populacao_municipal;
