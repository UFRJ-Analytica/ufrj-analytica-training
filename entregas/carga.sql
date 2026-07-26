-- carga.sql
-- UFRJ Analytica - Banco de Dados I
-- Trainee: Lucas Contreiras
-- Popula as tabelas finais a partir das tabelas raw_, na ordem pai -> filho

PRAGMA foreign_keys = ON;

-- 1. regioes (tabela pai)
INSERT INTO regioes (id_regiao, sigla_regiao, nome_regiao)
SELECT DISTINCT id_regiao, sigla_regiao, nome_regiao
FROM raw_regioes
WHERE id_regiao IS NOT NULL;

-- 2. estados (depende de regioes)
INSERT INTO estados (id_uf, sigla_uf, nome_uf, id_regiao)
SELECT DISTINCT id_uf, sigla_uf, nome_uf, id_regiao
FROM raw_estados
WHERE id_uf IS NOT NULL;

-- 3. municipios (depende de estados)
INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios
WHERE id_municipio IS NOT NULL;

-- 4. populacao_municipal (depende de municipios)
-- raw_populacao_municipal está em formato longo (indicador/valor/unidade/fonte),
-- então filtro pelo indicador de população residente estimada
INSERT INTO populacao_municipal (id_municipio, ano, populacao)
SELECT DISTINCT id_municipio, ano, valor
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL
  AND indicador = 'populacao_residente_estimada';
