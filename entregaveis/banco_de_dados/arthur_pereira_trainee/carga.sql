-- carga.sql
-- Defina aqui as instruções para carregar os dados das tabelas brutas para as tabelas normalizadas.
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

insert into estados (
id_uf,
sigla_uf,
nome_uf,
id_regiao)
select distinct 
id_uf,
sigla_uf,
nome_uf,
id_regiao
from raw_estados 
where id_uf is not null;

insert into municipios (
id_municipio,
nome_municipio,
id_uf)
select distinct
id_municipio,
nome_municipio,
id_uf
from raw_municipios 
where id_municipio is not null;

insert into populacao_municipal (
id_municipio,
ano,
valor)
select distinct
id_municipio,
ano,
valor
from raw_populacao_municipal 
where id_municipio is not null and ano is not null;
