PRAGMA foreign_keys = ON;

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
WHERE id_uf IS NOT NULL
  AND id_regiao IS NOT NULL;

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
WHERE id_municipio IS NOT NULL
  AND id_uf IS NOT NULL;

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
WHERE indicador IS NOT NULL
  AND unidade IS NOT NULL
  AND fonte IS NOT NULL;

INSERT INTO fato_indicador_municipal (
    id_municipio,
    id_indicador,
    ano,
    valor
)
SELECT DISTINCT
    rp.id_municipio,
    i.id_indicador,
    rp.ano,
    rp.valor
FROM raw_populacao_municipal AS rp
JOIN indicadores AS i
    ON i.nome_indicador = rp.indicador
   AND i.unidade = rp.unidade
   AND i.fonte = rp.fonte
WHERE rp.id_municipio IS NOT NULL
  AND rp.ano IS NOT NULL
  AND rp.valor IS NOT NULL;