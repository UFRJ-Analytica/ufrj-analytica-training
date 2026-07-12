-- analytics.sql — consultas analíticas (mín. 5)
-- Comparação, ranking, distribuição, classificação e concentração da população.
-- Modelo: regioes, estados(id_uf), municipios(id_uf), populacao_municipal.

PRAGMA foreign_keys = ON;

-- 1. Ranking: os 10 municípios mais populosos da base.
SELECT m.nome_municipio, e.sigla_uf, r.nome_regiao, p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
JOIN regioes    r ON r.id_regiao    = e.id_regiao
ORDER BY p.valor DESC
LIMIT 10;

-- 2. Distribuição: população total estimada por região.
SELECT r.nome_regiao, SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
JOIN regioes    r ON r.id_regiao    = e.id_regiao
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total DESC;

-- 3. Síntese: população média dos municípios por estado.
SELECT e.sigla_uf, e.nome_uf,
       COUNT(*)               AS qtd_municipios,
       ROUND(AVG(p.valor), 0) AS populacao_media_municipio
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_media_municipio DESC;

-- 4. Comparação: municípios acima da média nacional dos municípios (subconsulta).
SELECT m.nome_municipio, e.sigla_uf, p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
WHERE p.valor > (SELECT AVG(valor) FROM populacao_municipal)
ORDER BY p.valor DESC;

-- 5. Classificação (CASE) por porte e contagem por região.
SELECT r.nome_regiao,
       CASE
           WHEN p.valor < 50000   THEN 'pequeno (< 50 mil)'
           WHEN p.valor < 500000  THEN 'medio (50 mil a 500 mil)'
           ELSE                        'grande (>= 500 mil)'
       END AS porte,
       COUNT(*) AS qtd_municipios
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
JOIN regioes    r ON r.id_regiao    = e.id_regiao
GROUP BY r.nome_regiao, porte
ORDER BY r.nome_regiao, qtd_municipios DESC;

-- 6. Concentração: participação (%) de cada região na população nacional.
--    Proposta de camada analítica materializada como VIEW reutilizável.
DROP VIEW IF EXISTS vw_populacao_por_regiao;
CREATE VIEW vw_populacao_por_regiao AS
SELECT r.nome_regiao,
       SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
JOIN regioes    r ON r.id_regiao    = e.id_regiao
GROUP BY r.id_regiao, r.nome_regiao;

SELECT nome_regiao,
       populacao_total,
       ROUND(100.0 * populacao_total / (SELECT SUM(populacao_total) FROM vw_populacao_por_regiao), 2)
           AS percentual_nacional
FROM vw_populacao_por_regiao
ORDER BY populacao_total DESC;
