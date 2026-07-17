-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

PRAGMA foreign_keys = ON;

-- 1. Quais são os 10 municípios mais populosos?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    f.valor AS populacao
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
ORDER BY f.valor DESC
LIMIT 10;

-- 2. Quais são os municípios mais populosos do Rio Grande do Sul?
SELECT
    m.nome_municipio,
    f.valor AS populacao
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
WHERE e.sigla_uf = 'RS'
ORDER BY f.valor DESC;

-- 3. Qual é a população total por região?
SELECT
    r.nome_regiao,
    SUM(f.valor) AS populacao_total
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN regioes r
    ON e.id_regiao = r.id_regiao
GROUP BY r.nome_regiao
ORDER BY populacao_total DESC;

-- 4. Qual é a população média dos municípios por estado?
SELECT
    e.nome_uf,
    ROUND(AVG(f.valor),2) AS media_populacao
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
GROUP BY e.nome_uf
ORDER BY media_populacao DESC;

-- 5. Quais municípios possuem população acima da média nacional?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    f.valor
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
WHERE f.valor > (
    SELECT AVG(valor)
    FROM fato_indicador_municipal
)
ORDER BY f.valor DESC;