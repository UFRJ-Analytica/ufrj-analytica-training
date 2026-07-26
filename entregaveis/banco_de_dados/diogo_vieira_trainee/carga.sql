-- carga.sql
-- Defina aqui as instruções para carregar os dados das tabelas brutas para as tabelas normalizadas.
PRAGMA foreign_keys = ON;

DELETE FROM fato_indicador_municipal;
DELETE FROM indicadores;
DELETE FROM municipios;
DELETE FROM estados;
DELETE FROM regioes;

INSERT INTO regioes (
id_regiao,
sigla_regiao,
nome_regiao
)
SELECT DISTINCT
id_regiao,
sigla_regiao,
nome_regiao
FROM raw_regioes
WHERE id_regiao IS NOT NULL;

INSERT INTO indicadores (
indicador,
unidade,
fonte
)
SELECT DISTINCT
indicador,
unidade,
fonte
FROM raw_populacao_municipal
WHERE indicador IS NOT NULL;

INSERT INTO estados (
id_uf,
sigla_uf,
nome_uf,
id_regiao
)
SELECT DISTINCT
id_uf,
sigla_uf,
nome_uf,
id_regiao
FROM raw_estados
WHERE id_uf IS NOT NULL;

INSERT INTO municipios (
id_municipio,
nome_municipio,
id_uf
)
SELECT DISTINCT
id_municipio,
nome_municipio,
id_uf
FROM raw_municipios
WHERE id_municipio IS NOT NULL;

INSERT INTO fato_indicador_municipal (
id_municipio,
indicador,
ano,
valor
)
SELECT DISTINCT
id_municipio,
indicador,
ano,
valor
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL
AND indicador IS NOT NULL
AND ano IS NOT NULL;