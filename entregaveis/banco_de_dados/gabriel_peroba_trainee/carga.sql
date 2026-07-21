PRAGMA foreign_keys = ON;

--Regioes
INSERT INTO regioes (id_regiao, sigla_regiao, nome_regiao)
SELECT DISTINCT id_regiao, sigla_regiao, nome_regiao
FROM raw_regioes
WHERE id_regiao IS NOT NULL;

-- Estados
INSERT INTO estados (id_uf, sigla_uf, nome_uf, id_regiao)
SELECT DISTINCT id_uf, sigla_uf, nome_uf, id_regiao
FROM raw_estados
WHERE id_uf IS NOT NULL;

-- Municipios
INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios
WHERE id_municipio IS NOT NULL;

-- 4. Populacao
INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
SELECT DISTINCT id_municipio, ano, indicador, valor, unidade, fonte
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL;