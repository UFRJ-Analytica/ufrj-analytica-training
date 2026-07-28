-- carga.sql
PRAGMA foreign_keys = ON;

-- região
INSERT INTO regiao (
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

-- UF
INSERT INTO UF (
    id_uf,
    id_regiao,
    sigla_uf,
    nome_uf
)
SELECT DISTINCT
    id_uf,
    id_regiao,
    sigla_uf,
    nome_uf
FROM raw_estados
WHERE id_uf IS NOT NULL;

--municipio
INSERT INTO Municipios (
    id_municipio,
    id_uf,
    nome_municipio
)
SELECT DISTINCT
    id_municipio,
    id_uf,
    nome_municipio
FROM raw_municipios
WHERE id_municipio IS NOT NULL;

-- fnte
INSERT INTO fonte (
    nome
)
SELECT DISTINCT
    fonte
FROM raw_populacao_municipal;

-- censo
INSERT INTO censo (
    Ano,
    id_fonte,
    id_municipio,
    valor
)
SELECT 
    raw.ano,
    f.id_fonte,       
    raw.id_municipio, 
    raw.valor   
FROM raw_populacao_municipal raw
JOIN fonte f ON f.nome = raw.fonte;