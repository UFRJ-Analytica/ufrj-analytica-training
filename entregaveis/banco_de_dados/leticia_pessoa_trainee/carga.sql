-- carga.sql
-- Defina aqui as instruções para carregar os dados das tabelas brutas para as tabelas normalizadas.

-- Popular regioes
INSERT INTO regioes (id_regiao, sigla_regiao, nome_regiao)
SELECT DISTINCT id_regiao, sigla_regiao, nome_regiao
FROM raw_municipios_com_populacao
WHERE id_regiao IS NOT NULL;

-- Popular estados
INSERT INTO estados (id_uf, sigla_uf, nome_uf, id_regiao)
SELECT DISTINCT id_uf, sigla_uf, nome_uf, id_regiao
FROM raw_municipios_com_populacao
WHERE id_uf IS NOT NULL AND id_regiao IS NOT NULL;

-- Popular municipios
INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios_com_populacao
WHERE id_municipio IS NOT NULL AND id_uf IS NOT NULL;

-- Popular populacoes
INSERT INTO populacao (id_municipio, ano, valor_populacao)
SELECT DISTINCT id_municipio, ano, valor
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL AND ano IS NOT NULL;