-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- Quais são os municípios mais populosos da base?

SELECT
	m.nome_municipio,
	f.valor AS populacao_total
FROM municipios m
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
GROUP BY m.id_municipio
ORDER BY populacao_total DESC
LIMIT 10;

-- Quais são os municípios mais populosos de uma UF escolhida?

SELECT
m.nome_municipio,
f.valor AS populacao_total
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
WHERE e.id_uf = 35 -- ID do RJ
ORDER BY populacao_total DESC
LIMIT 10;

-- Qual é a população total estimada por região?

SELECT
	r.nome_regiao,
	SUM(f.valor) AS populacao_total
FROM regioes r
JOIN estados e ON e.id_regiao = r.id_regiao
JOIN municipios m ON m.id_uf = e.id_uf
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
GROUP BY r.nome_regiao

UNION ALL

SELECT
    'TOTAL' AS nome_regiao,
    SUM(f.valor) AS populacao_total
FROM fato_indicador_municipal f;

-- Qual é a população média dos municípios por estado? 

SELECT
	e.nome_uf,
	SUM(f.valor) / COUNT(m.id_municipio) AS media_populacao
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
GROUP BY e.nome_uf
ORDER BY media_populacao DESC;

-- Quais municípios possuem população acima da média nacional dos municípios?

SELECT
	m.nome_municipio,
	f.valor AS populacao
FROM municipios m
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
WHERE f.valor > (SELECT AVG(valor) FROM fato_indicador_municipal);

-- Qual região concentra a maior população estimada?

SELECT
	r.nome_regiao,
	SUM(f.valor) AS populacao_total
FROM regioes r
JOIN estados e ON e.id_regiao = r.id_regiao
JOIN municipios m ON m.id_uf = e.id_uf
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
GROUP BY r.nome_regiao
ORDER BY populacao_total DESC
LIMIT 1;

-- Quais estados possuem maior concentração populacional em poucos municípios?

-- O cálculo foi feito utilizando a maior cidade em população do estado e dividindo a população total pela população dessa maior cidade, assim obtendo a concentração nesse caso.
WITH populacao_estado AS (
    SELECT 
        e.id_uf,
        e.nome_uf,
        SUM(f.valor) AS populacao_total
    FROM estados e
    JOIN municipios m ON e.id_uf = m.id_uf
    JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
    GROUP BY e.id_uf, e.nome_uf
),
maior_municipio AS (
    SELECT 
        e.id_uf,
        MAX(f.valor) AS populacao_maior_municipio
    FROM estados e
    JOIN municipios m ON e.id_uf = m.id_uf
    JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
    GROUP BY e.id_uf
)
SELECT
    p.nome_uf,
    p.populacao_total,
    mm.populacao_maior_municipio,
    ROUND(100.0 * mm.populacao_maior_municipio / p.populacao_total, 1) AS pct_concentracao
FROM populacao_estado p
JOIN maior_municipio mm ON p.id_uf = mm.id_uf
ORDER BY pct_concentracao DESC;













