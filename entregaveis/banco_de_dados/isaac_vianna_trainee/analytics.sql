-- analytics.sql
-- Consultas analiticas: rankings, agregacoes, classificacao e camada analitica (view).

PRAGMA foreign_keys = ON;

-- 1. Ranking dos 10 municipios mais populosos do pais.
SELECT
    m.nome_municipio,
    e.sigla_uf,
    p.valor AS populacao_estimada,
    RANK() OVER (ORDER BY p.valor DESC) AS ranking_nacional
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
ORDER BY p.valor DESC
LIMIT 10;

-- 2. Populacao total estimada por regiao.
SELECT
    r.nome_regiao,
    SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total DESC;

-- 3. Populacao media dos municipios por estado.
SELECT
    e.sigla_uf,
    e.nome_uf,
    ROUND(AVG(p.valor), 1) AS populacao_media_municipio,
    COUNT(m.id_municipio) AS qtd_municipios
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_media_municipio DESC;

-- 4. Municipios com populacao acima da media nacional (subconsulta).
SELECT
    m.nome_municipio,
    e.sigla_uf,
    p.valor AS populacao_estimada
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
WHERE p.valor > (SELECT AVG(valor) FROM populacao_municipal)
ORDER BY p.valor DESC;

-- 5. Classificacao dos municipios por porte populacional e contagem por regiao.
SELECT
    r.nome_regiao,
    CASE
        WHEN p.valor < 20000 THEN 'pequeno'
        WHEN p.valor < 100000 THEN 'medio'
        ELSE 'grande'
    END AS porte,
    COUNT(*) AS qtd_municipios
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.nome_regiao, porte
ORDER BY r.nome_regiao, porte;

-- 6. Camada analitica: view com a participacao percentual de cada regiao
--    na populacao nacional.
DROP VIEW IF EXISTS vw_populacao_por_regiao;

CREATE VIEW vw_populacao_por_regiao AS
SELECT
    r.nome_regiao,
    SUM(p.valor) AS populacao_total,
    ROUND(
        100.0 * SUM(p.valor) / (SELECT SUM(valor) FROM populacao_municipal),
        2
    ) AS percentual_nacional
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.id_regiao, r.nome_regiao;

SELECT * FROM vw_populacao_por_regiao
ORDER BY percentual_nacional DESC;
