-- analytics.sql


-- 1. Quais são os 10 municípios mais populosos da base?
SELECT
    muni.nome_municipio AS municipio,
    est.sigla_uf AS uf,
    popu.ano,
    popu.valor AS populacao
FROM populacao_municipal popu
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
ORDER BY populacao DESC
LIMIT 10;

-- 2. Quais são os 10 municípios mais populosos do Rio de Janeiro?
SELECT
    muni.nome_municipio AS  municipio,
    popu.ano,
    popu.valor AS populacao
FROM populacao_municipal popu
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
WHERE est.sigla_uf = 'RJ'
ORDER BY populacao DESC
LIMIT 10;


-- 3. Qual é a população total estimada por região?
SELECT
    reg.nome_regiao AS regiao,
    popu.ano,
    SUM (popu.valor) AS populacao_total
FROM populacao_municipal popu
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
JOIN regioes reg ON est.id_regiao = reg.id_regiao
GROUP BY reg.nome_regiao, popu.ano
ORDER BY populacao_total DESC;


-- 4. Qual é a população média dos municípios por estado?
SELECT
    est.nome_uf AS estado,
    popu.ano,
    ROUND( AVG(popu.valor),2) AS populacao_media
FROM populacao_municipal popu
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
GROUP BY est.nome_uf, popu.ano
ORDER BY populacao_media DESC;


-- 5. Quais municípios possuem população acima da média nacional dos municípios?
SELECT
    muni.nome_municipio AS municipio,
    est.sigla_uf AS uf,
    popu.valor AS populacao
FROM populacao_municipal popu
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
WHERE popu.valor > (
    SELECT AVG (valor)
    FROM populacao_municipal
)
ORDER BY populacao DESC;


-- 6. Quantos municípios pequenos, médios e grandes existem na base?
SELECT
    CASE
        WHEN popu.valor < 30000 THEN 'Pequeno'
        WHEN popu.valor <= 150000 THEN 'Medio'
        ELSE 'Grande'
    END AS porte,
    COUNT( *) AS quantidade_municipios
FROM populacao_municipal popu
GROUP BY porte
ORDER BY quantidade_municipios DESC;


-- 7. Quantos municípios pequenos, médios e grandes existem por região?
SELECT
    reg.nome_regiao AS regiao,
    CASE
        WHEN popu.valor < 30000 THEN 'Pequeno'
        WHEN popu.valor <= 150000 THEN 'Medio'
        ELSE 'Grande'
    END AS porte,
    COUNT( *) AS quantidade_municipios
FROM populacao_municipal popu
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
JOIN regioes reg ON est.id_regiao = reg.id_regiao
GROUP BY reg.nome_regiao, porte
ORDER BY regiao, quantidade_municipios DESC;