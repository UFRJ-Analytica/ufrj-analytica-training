-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- 1. Quais são os municípios mais populosos da base?
SELECT
    m.nome_municipio,
    SUM(p.valor) as pop_total
FROM municipios m
INNER JOIN populacao_municipal p
ON m.id_municipio = p.id_municipio
GROUP BY m.nome_municipio
ORDER BY p.valor DESC
LIMIT 5;
-- Os 5 municípios mais populosos da base são: São Paulo, Rio de Janeiro, Brasília, Fortaleza e Salvador


-- 3. Qual é a população total estimada por região?
SELECT 
    r.nome_regiao,
    SUM(p.valor) as pop_total
FROM regioes r
INNER JOIN estados e
ON e.id_regiao = r.id_regiao
INNER JOIN municipios m
ON m.id_uf = e.id_uf
INNER JOIN populacao_municipal p
ON p.id_municipio = m.id_municipio
GROUP BY r.nome_regiao
ORDER BY p.valor DESC;
-- A população estimada por região é: Nodeste = 57244485, Norte = 18801282, Centro-Oeste = 17232941, Sul = 31310809, Sudeste = 88825643.

-- 5. Quais municípios possuem população acima da média nacional dos municípios?
--> criando a CTE ("bloco preparatório")
WITH media_nacional as ( -- media_nacional vai se comportar como uma tabela temporária
    SELECT 
        AVG(p.valor) as media 
    FROM populacao_municipal p
)
SELECT
    m.nome_municipio,
    p.valor
FROM municipios m
INNER JOIN populacao_municipal p
ON m.id_municipio = p.id_municipio
CROSS JOIN media_nacional n -- combina linha de uma tabela com todas as linhas de outra
WHERE p.valor > n.media
ORDER BY p.valor DESC, p.ano;

/*
ON m.id_municipio = p.id_municipio
WHERE p.valor > (
    SELECT AVG(p.valor)
    FROM populacao_municial p >> fazendo um SELECT no WHERE (subquery)
);
*/

-- 7. Quantos municípios pequenos, médios e grandes existem por região?
SELECT
    CASE 
        WHEN p.valor < 20000 THEN '1) Município pequeno (< 20k habitantes)'
        WHEN p.valor < 100000 THEN '2) Município médio (20k a 100k habitantes)'
        ELSE '3) Município grande (> 100k habitantes)'
    END as porte, -- dá o nome pra coluna criada (cada linha vai ter "1) Município pequeno..." com o nome da coluna com as categorias de "porte")
    COUNT(*) as qntd_municipios -- conta quantos municipios em cada porte e salva essa coluna com a quantidade como "qntd_municipios"
FROM populacao_municipal p
GROUP BY porte
ORDER BY porte;
-- São 3818 municípios pequenos, 1414 médios e 338 grandes.

-- 8. Qual região concentra a maior população estimada?
SELECT
    r.nome_regiao,
    SUM(p.valor) as pop_estimada
FROM regioes r
INNER JOIN estados e
ON e.id_regiao = r.id_regiao
INNER JOIN municipios m
ON e.id_uf = m.id_uf
INNER JOIN populacao_municipal p
ON p.id_municipio = m.id_municipio
GROUP BY r.nome_regiao
ORDER BY p.valor DESC
LIMIT 1;
-- a região com maior população é a região é o Nordeste 