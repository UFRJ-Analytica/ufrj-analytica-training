-- carga.sql
-- preenche tabela q criei no schema
-- dicas do exercicio: 
-- preencher primeiro as pai dps as filhas (ent ordem eh regiao -> estado -> municipio -> populacao_municipal)
-- INSERT INTO ... SELECT (leva dados da raw pras tabelas finais)
-- SELECT DISTINCT pra remover repeticoes


PRAGMA foreign_keys = ON;
DELETE FROM populacao_municipal;
DELETE FROM municipios;
DELETE FROM estados;
DELETE FROM regioes;


INSERT INTO regioes (id_regiao, sigla_regiao,nome_regiao) -- coloca as colunas da tabela q quero preencher
SELECT DISTINCT id_regiao, sigla_regiao, nome_regiao -- distinct: se tira linha repetida se tiver
FROM raw_regioes -- insert vai inserir da tabela raw_regioes
WHERE id_regiao IS NOT NULL -- copia apenas linha q tem id_regiao sem ser nulo
  AND sigla_regiao IS NOT NULL
  AND nome_regiao IS NOT NULL;


INSERT INTO estados (id_uf, nome_uf, sigla_uf, id_regiao)
SELECT DISTINCT id_uf, nome_uf, sigla_uf, id_regiao
FROM raw_estados
WHERE id_uf IS NOT NULL
  AND sigla_uf IS NOT NULL
  AND nome_uf IS NOT NULL
  AND id_regiao IS NOT NULL;


INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios
WHERE id_municipio IS NOT NULL
  AND nome_municipio IS NOT NULL
  AND id_uf IS NOT NULL;


INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
SELECT DISTINCT id_municipio, ano, indicador, valor, unidade, fonte
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL
  AND ano IS NOT NULL
  AND valor IS NOT NULL
  AND indicador IS NOT NULL; 