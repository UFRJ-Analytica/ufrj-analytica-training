PRAGMA foreign_keys = ON;

INSERT INTO regiao(
	id_regiao,
	sigla_regiao,
	nome_regiao
)
SELECT DISTINCT
	id_regiao,
	sigla_regiao,
	nome_regiao
FROM raw_regioes WHERE id_regiao IS NOT NULL;

INSERT INTO estado(
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
FROM raw_estados WHERE id_uf IS NOT NULL;

INSERT INTO municipio(
	id_municipio,
	nome_municipio,
	id_estado
)
SELECT DISTINCT
	id_municipio,
	nome_municipio,
	id_uf
FROM raw_municipios WHERE id_municipio IS NOT NULL;

INSERT INTO censo(
	ano,
	indicador,
	unidade,
	fonte
)
SELECT DISTINCT
	ano,
	indicador,
	unidade,
	fonte
FROM raw_municipios_com_populacao;

INSERT INTO populacao_municipal(
	id_municipio,
	valor,
	id_censo
)
SELECT DISTINCT
	id_municipio,
	valor,
	id_censo
FROM raw_municipios_com_populacao r
inner join censo c on c.indicador=r.indicador
WHERE id_municipio IS NOT NULL;