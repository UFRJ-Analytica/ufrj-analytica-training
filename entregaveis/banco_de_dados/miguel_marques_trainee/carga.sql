-- carga.sql
-- Defina aqui as instruções para carregar os dados das tabelas brutas para as tabelas normalizadas.
PRAGMA foreign_keys = ON;


-- 1. Carrega regiões
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



-- 2. Carrega estados
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



-- 3. Carrega municípios
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



-- 4. Carrega indicadores
-- Cada combinação representa um indicador disponível
INSERT INTO indicadores (
    nome_indicador,
    unidade,
    fonte
)
SELECT DISTINCT
    indicador,
    unidade,
    fonte
FROM raw_populacao_municipal
WHERE indicador IS NOT NULL;



-- 5. Carrega fatos populacionais
INSERT INTO fato_indicador_municipal (
    id_municipio,
    id_indicador,
    ano,
    valor
)
SELECT DISTINCT
    p.id_municipio,
    i.id_indicador,
    p.ano,
    p.valor
FROM raw_populacao_municipal p
JOIN indicadores i
    ON p.indicador = i.nome_indicador
    AND p.unidade = i.unidade
    AND p.fonte = i.fonte
WHERE p.id_municipio IS NOT NULL;