-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- 1. Quais são os municípios mais populosos da base?
SELECT m.nome_municipio, f.ano, f.valor
FROM fato_indicador_municipal f
JOIN municipios m
ON f.id_municipio = m.id_municipio
ORDER BY f.valor DESC
LIMIT 50;

-- 3. Qual é a população total estimada por região?
SELECT r.nome_regiao, SUM(f.valor) as populacao, f.ano
FROM fato_indicador_municipal f
JOIN municipios m
ON f.id_municipio = m.id_municipio
JOIN estados e
ON m.id_uf = e.id_uf
JOIN regioes r
ON e.id_regiao = r.id_regiao
WHERE f.indicador = 'populacao_residente_estimada'
GROUP BY r.id_regiao, f.ano;

-- 4. Qual é a população média dos municípios por estado?
SELECT e.nome_uf, ROUND(AVG(f.valor)) as populacao_media_municipal, f.ano
FROM fato_indicador_municipal f
JOIN municipios m
ON f.id_municipio = m.id_municipio
JOIN estados e
ON m.id_uf = e.id_uf
WHERE f.indicador = 'populacao_residente_estimada'
GROUP BY e.id_uf, f.ano
ORDER BY e.nome_uf;

-- 5. Quais municípios possuem população acima da média nacional dos municípios?
SELECT m.nome_municipio, f.valor,
(SELECT AVG(valor) FROM fato_indicador_municipal) AS media_nacional
FROM municipios m
JOIN fato_indicador_municipal f
ON f.id_municipio = m.id_municipio
WHERE f.valor > (
    SELECT AVG(valor)
    FROM fato_indicador_municipal
)
ORDER BY f.valor;

-- 8. Qual região concentra a maior população estimada?
SELECT r.nome_regiao, SUM(f.valor) as populacao, f.ano
FROM fato_indicador_municipal f
JOIN municipios m
ON f.id_municipio = m.id_municipio
JOIN estados e
ON m.id_uf = e.id_uf
JOIN regioes r
ON e.id_regiao = r.id_regiao
WHERE f.indicador = 'populacao_residente_estimada'
GROUP BY r.id_regiao, f.ano
ORDER BY populacao DESC
LIMIT 1;