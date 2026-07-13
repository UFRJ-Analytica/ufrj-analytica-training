-- analytics.sql

-- 1. Quais são os 10 municípios mais populosos da base?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    p.valor AS populacao_estimada
FROM populacao_municipal AS p
JOIN municipios AS m
    ON p.id_municipio = m.id_municipio
JOIN estados AS e
    ON m.id_uf = e.id_uf
ORDER BY p.valor DESC
LIMIT 10;

-- 2. Qual é a população total estimada por região?

SELECT
    r.nome_regiao,
    SUM(p.valor) AS populacao_total_estimada
FROM regioes AS r
JOIN estados AS e
    ON r.id_regiao = e.id_regiao
JOIN municipios AS m
    ON e.id_uf = m.id_uf
JOIN populacao_municipal AS p
    ON m.id_municipio = p.id_municipio
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total_estimada DESC;

-- 3. Qual é a população média dos municípios por estado?

SELECT
    e.nome_uf,
    AVG(p.valor) AS populacao_media_municipios
FROM estados AS e
JOIN municipios AS m
    ON e.id_uf = m.id_uf
JOIN populacao_municipal AS p
    ON m.id_municipio = p.id_municipio
GROUP BY e.id_uf, e.nome_uf
ORDER BY populacao_media_municipios DESC;

-- 4. Quais os 30 que municípios possuem população acima da média nacional dos municípios?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    p.valor AS populacao_estimada
FROM populacao_municipal AS p
JOIN municipios AS m
    ON p.id_municipio = m.id_municipio
JOIN estados AS e
    ON m.id_uf = e.id_uf
WHERE p.valor > (
    SELECT AVG(valor)
    FROM populacao_municipal
)
ORDER BY p.valor DESC
LIMIT 30;

-- 5. Quantos municípios pequenos, médios e grandes existem na base?
-- Pequenos = possui menos de 50.000 habitantes; Médios = possui entre 50.000 e 500.000 habitantes; Grande = acima de 500.000 habitantes

SELECT
    CASE
        WHEN valor < 50000 THEN 'Pequeno'
        WHEN valor < 500000 THEN 'Médio'
        ELSE 'Grande'
    END AS porte_municipio,
    COUNT(*) AS quantidade_municipios
FROM populacao_municipal
GROUP BY porte_municipio
ORDER BY quantidade_municipios DESC;

-- 6. Quantos municípios pequenos, médios e grandes existem por região?

SELECT
    r.nome_regiao,
    CASE
        WHEN p.valor < 50000 THEN 'Pequeno'
        WHEN p.valor < 500000 THEN 'Médio'
        ELSE 'Grande'
    END AS porte_municipio,
    COUNT(*) AS quantidade_municipios
FROM populacao_municipal AS p
JOIN municipios AS m
    ON p.id_municipio = m.id_municipio
JOIN estados AS e
    ON m.id_uf = e.id_uf
JOIN regioes AS r
    ON e.id_regiao = r.id_regiao
GROUP BY
    r.id_regiao,
    r.nome_regiao,
    porte_municipio
ORDER BY
    r.nome_regiao,
    quantidade_municipios DESC;