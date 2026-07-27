-- carga.sql
-- Defina aqui as instruções para carregar os dados das tabelas brutas para as tabelas normalizadas.

-- popular as tabelas criadas com os dados das tabelas raw

PRAGMA foreign_keys = ON;

/*
	 Modelo:
	 
 INSERT INTO tabela que criei (
	[tudo que tem nela]
)
SELECT DISTINCT
	[tudo que tem nela e na raw]
FROM tabela raw
WHERE primary key IS NOT NULL

*/

INSERT INTO regioes (
    id_regiao,
    sigla_regiao,
    nome_regiao
)
SELECT DISTINCT -- pra remover repetições
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
WHERE id_uf IS NOT NULL and id_regiao IS NOT NULL;

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
WHERE id_municipio IS NOT NULL and id_uf IS NOT NULL; -- a chave primaria e achave estrangeira not null

INSERT INTO populacao_municipal (
	ano,
	indicador,
	valor,
	unidade,
	fonte,
	id_municipio
)
SELECT DISTINCT 
	ano,
	indicador,
	valor,
	unidade,
	fonte,
	id_municipio
FROM raw_municipios_com_populacao
WHERE id_municipio IS NOT NULL;




