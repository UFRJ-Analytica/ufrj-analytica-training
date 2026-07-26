-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- 1. Quais são os municípios mais populosos da base (Top 10)?
-- Utiliza ordenação descendente e limite para criar um ranking nacional.
SELECT 
    m.nome_municipio, 
    e.sigla_uf, 
    p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
WHERE p.ano = 2021
ORDER BY p.valor DESC
LIMIT 10;

-- 2. Qual é a população total estimada por região?
-- Agrupa os dados por região e soma a população de todos os seus municípios.
SELECT 
    r.nome_regiao, 
    SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
WHERE p.ano = 2021
GROUP BY r.nome_regiao
ORDER BY populacao_total DESC;

-- 3. Qual é a população média dos municípios por estado?
-- Tira a média (AVG) da população dos municípios dentro de cada estado.
SELECT 
    e.nome_uf, 
    ROUND(AVG(p.valor), 0) AS populacao_media_por_municipio
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
WHERE p.ano = 2021
GROUP BY e.nome_uf
ORDER BY populacao_media_por_municipio DESC;

-- 4. Quais municípios possuem população acima da média nacional dos municípios?
-- Utiliza uma sub-query: primeiro o banco calcula a média nacional, 
-- depois filtra apenas os municípios que estão acima desse valor.
SELECT 
    m.nome_municipio, 
    e.sigla_uf, 
    p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
WHERE p.ano = 2021 
  AND p.valor > (SELECT AVG(valor) FROM populacao_municipal WHERE ano = 2021)
ORDER BY p.valor DESC;

-- 5. Quantos municípios pequenos, médios e grandes existem na base?
-- Utiliza a cláusula CASE WHEN para classificar o tamanho do município 
-- com base na sua população e depois conta quantos existem em cada categoria.
SELECT 
    CASE 
        WHEN p.valor <= 50000 THEN '1 - Pequeno (Até 50 mil hab.)'
        WHEN p.valor <= 500000 THEN '2 - Médio (50 mil a 500 mil hab.)'
        ELSE '3 - Grande (Mais de 500 mil hab.)'
    END AS porte_municipio,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
WHERE p.ano = 2021
GROUP BY porte_municipio
ORDER BY porte_municipio;