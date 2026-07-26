
PRAGMA foreign_keys = ON;

--1.Popular regioes
INSERT INTO regioes (id_regiao, sigla_regiao, nome_regiao)
SELECT DISTINCT id_regiao, sigla_regiao, nome_regiao
FROM raw_regioes
WHERE id_regiao IS NOT NULL;

--2.Popular estados
INSERT INTO estados (id_uf, sigla_uf, nome_uf, id_regiao)
SELECT DISTINCT id_uf, sigla_uf, nome_uf, id_regiao
FROM raw_estados;

--3.Popular municipios
INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios;

--4.Popular populacao
INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
SELECT id_municipio, ano, indicador, valor, unidade, fonte
FROM raw_populacao_municipal;