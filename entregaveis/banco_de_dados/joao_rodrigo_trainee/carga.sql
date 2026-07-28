PRAGMA foreign_keys = ON;

INSERT INTO regioes 
SELECT DISTINCT * FROM raw_regioes
WHERE id_regiao IS NOT NULL;

INSERT INTO estados 
SELECT DISTINCT
	id_uf, 
	sigla_uf, 
	nome_uf, 
	id_regiao 
FROM raw_estados
WHERE id_uf IS NOT NULL;

INSERT INTO municipios 
SELECT DISTINCT
	id_municipio, 
	nome_municipio, 
	id_uf 
FROM raw_municipios
WHERE id_municipio IS NOT NULL;

INSERT INTO populacao_municipal 
SELECT DISTINCT
	id_municipio, 
	ano, 
	indicador, 
	valor, 
	unidade, 
	fonte 
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL;


