-- carga.sql
-- Defina aqui as instruções para carregar os dados das tabelas brutas para as tabelas normalizadas.
PRAGMA foreign_keys = ON;

--popula regiao
INSERT INTO regiao (id, sigla, nome)
SELECT DISTINCT 
    id_regiao, 
    sigla_regiao, 
    nome_regiao
FROM raw_regioes
WHERE id_regiao IS NOT NULL;

--popula estados
INSERT INTO estado (id, sigla, nome, id_regiao)
SELECT DISTINCT 
    id_uf, 
    sigla_uf, 
    nome_uf, 
    id_regiao
FROM raw_estados
WHERE id_uf IS NOT NULL;

--popula municipio
INSERT INTO municipio (id, nome, id_estado)
SELECT DISTINCT 
    id_municipio, 
    nome_municipio, 
    id_uf
FROM raw_municipios
WHERE id_municipio IS NOT NULL;

--popula relatorio_populacao
INSERT INTO relatorio_populacao (ano, id_municipio, indicador, valor, unidade, fonte)
SELECT DISTINCT 
    ano, 
    id_municipio, 
    indicador, 
    valor, 
    unidade, 
    fonte
FROM raw_populacao_municipal
WHERE ano IS NOT NULL 
  AND id_municipio IS NOT NULL;