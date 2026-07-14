-- carga.sql

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
	WHERE id_regiao IS NOT NULL AND id_uf IS NOT NULL;
	
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
	WHERE id_uf IS NOT NULL AND id_municipio IS NOT NULL;
	
INSERT INTO indicadores (
	nome_indicador,
	unidade
)
	SELECT DISTINCT
		indicador,
		unidade
	FROM raw_populacao_municipal
	WHERE indicador IS NOT NULL;

INSERT INTO fato_indicador_municipal (
	id_municipio,
	id_indicador,
	ano,
	valor,
	fonte
)
	SELECT DISTINCT
		p.id_municipio,
		i.id_indicador,
		p.ano,
		p.valor,
		p.fonte
	FROM raw_populacao_municipal p
	INNER JOIN indicadores i ON i.nome_indicador = p.indicador AND i.unidade = p.unidade
	WHERE p.ano IS NOT NULL AND p.id_municipio IS NOT NULL;

