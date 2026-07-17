-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1. População total por estado
SELECT  
    est.sigla_uf,
    SUM(pop.valor_populacao) AS populacao_total_estado
FROM estados est
JOIN municipios mun ON est.id_uf = mun.id_uf
JOIN populacao pop ON mun.id_municipio = pop.id_municipio
GROUP BY est.id_uf, est.nome_uf, est.sigla_uf -- Assim ele mostra todas essas informações após agrupar
ORDER BY populacao_total_estado DESC;

-- 2. População total por região do brasil
SELECT 
    reg.nome_regiao,
    SUM(pop.valor_populacao) AS populacao_regional
FROM regioes reg
JOIN estados est ON reg.id_regiao = est.id_regiao
JOIN municipios mun ON est.id_uf = mun.id_uf
JOIN populacao pop ON mun.id_municipio = pop.id_municipio
GROUP BY reg.id_regiao, reg.nome_regiao
ORDER BY populacao_regional DESC;

-- 3. Média populacional dos municipios por estado
SELECT
    est.sigla_uf,
    ROUND(AVG(pop.valor_populacao), 0) AS media_habitantes_por_municipio
FROM estados est
JOIN municipios mun ON est.id_uf = mun.id_uf
JOIN populacao pop ON mun.id_municipio = pop.id_municipio
GROUP BY est.id_uf, est.nome_uf, est.sigla_uf
ORDER BY media_habitantes_por_municipio DESC;

-- ===========
--    CRUD
-- ===========

-- 4. INSERT
INSERT INTO populacao (id_municipio, ano, valor_populacao)
SELECT id_municipio, 2026, 632001
FROM municipios
WHERE nome_municipio = 'Rio de Janeiro';

-- 5. UPDATE: Alterar insert que acabou de ser feito
UPDATE populacao
SET valor_populacao = 5000000
WHERE ano = 2026
    AND id_municipio = (SELECT id_municipio FROM municipios WHERE nome_municipio = 'Rio de Janeiro');

-- 6. DELETE
DELETE FROM populacao
WHERE ano = 2026
    AND id_municipio = (SELECT id_municipio FROM municipios WHERE nome_municipio = 'Rio de Janeiro');