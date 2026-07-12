-- carga.sql
-- Popula as tabelas finais (schema.sql) a partir das tabelas brutas raw_.
-- Ordem: tabelas pai primeiro (regioes, estados, municipios, indicadores),
-- depois a tabela fato que depende delas.

PRAGMA foreign_keys = ON;

-- 1. regioes <- raw_regioes
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

-- 2. estados <- raw_estados
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

-- 3. municipios <- raw_municipios
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

-- 4. indicadores <- raw_populacao_municipal
-- Extrai o(s) indicador(es) presentes na base bruta, com sua unidade e fonte.
INSERT INTO indicadores (
    codigo,
    unidade,
    fonte
)
SELECT DISTINCT
    indicador,
    unidade,
    fonte
FROM raw_populacao_municipal
WHERE indicador IS NOT NULL;

-- 5. fato_indicador_municipal <- raw_populacao_municipal
-- Junta com indicadores para trocar o texto do indicador pelo id_indicador.
INSERT INTO fato_indicador_municipal (
    id_municipio,
    id_indicador,
    ano,
    valor
)
SELECT DISTINCT
    r.id_municipio,
    i.id_indicador,
    r.ano,
    r.valor
FROM raw_populacao_municipal r
JOIN indicadores i ON i.codigo = r.indicador
WHERE r.id_municipio IS NOT NULL
  AND r.ano IS NOT NULL
  AND r.valor IS NOT NULL;
