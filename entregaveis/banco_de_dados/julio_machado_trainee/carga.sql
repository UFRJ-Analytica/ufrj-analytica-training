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

INSERT INTO censos (
 ano,
 fonte
)
SELECT DISTINCT
 ano,
 fonte
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL;

INSERT INTO recenseamento (
 id_censo,
 id_municipio,
 valor,
 unidade
)
SELECT DISTINCT
 censos.id_censo,
 raw_populacao_municipal.id_municipio,
 raw_populacao_municipal.valor,
 raw_populacao_municipal.unidade
FROM raw_populacao_municipal
INNER JOIN censos 
	ON raw_populacao_municipal.ano = censos.ano AND raw_populacao_municipal.fonte = censos.fonte
WHERE id_municipio AND id_censo IS NOT NULL;