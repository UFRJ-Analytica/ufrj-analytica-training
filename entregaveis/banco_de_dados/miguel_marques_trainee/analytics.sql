-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.
PRAGMA foreign_keys = ON;

PRAGMA foreign_keys = ON;



-- 1. Quais são os 10 municípios mais populosos da base?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    f.valor AS populacao
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN indicadores i
    ON f.id_indicador = i.id_indicador
WHERE i.nome_indicador = 'População'
ORDER BY populacao DESC
LIMIT 10;



-- 2. Qual é a população total estimada por região?

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
JOIN indicadores i
    ON f.id_indicador = i.id_indicador
WHERE i.nome_indicador = 'População'
GROUP BY r.nome_regiao
ORDER BY populacao_total DESC;



-- 3. Qual é a população média dos municípios por estado?

SELECT
    e.nome_uf,
    AVG(f.valor) AS media_populacao
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN indicadores i
    ON f.id_indicador = i.id_indicador
WHERE i.nome_indicador = 'População'
GROUP BY e.nome_uf
ORDER BY media_populacao DESC;



-- 4. Quais municípios possuem população acima da média nacional?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    f.valor AS populacao
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN indicadores i
    ON f.id_indicador = i.id_indicador
WHERE i.nome_indicador = 'População'
AND f.valor > (
    SELECT AVG(valor)
    FROM fato_indicador_municipal
)
ORDER BY populacao DESC;



-- 5. Qual região concentra a maior população estimada?

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
JOIN indicadores i
    ON f.id_indicador = i.id_indicador
WHERE i.nome_indicador = 'População'
GROUP BY r.nome_regiao
ORDER BY populacao_total DESC
LIMIT 1;