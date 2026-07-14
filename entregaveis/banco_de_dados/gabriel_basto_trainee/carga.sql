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

INSERT INTO estados(
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

INSERT INTO municipios(
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
JOIN indicadores i
    ON i.nome_indicador = r.indicador
   AND (i.unidade = r.unidade OR (i.unidade IS NULL AND r.unidade IS NULL))
   AND (i.fonte = r.fonte OR (i.fonte IS NULL AND r.fonte IS NULL))
WHERE r.id_municipio IS NOT NULL;
