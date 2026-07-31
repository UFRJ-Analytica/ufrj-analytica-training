-- Quais são os municípios mais populosos da base (TOP 10)? 
SELECT
    municipios.nome_municipio,
    estados.nome_uf,
    populacao_municipal.valor AS populacao
FROM populacao_municipal
JOIN municipios
ON populacao_municipal.id_municipio = municipios.id_municipio
JOIN estados
ON municipios.id_uf = estados.id_uf
ORDER BY populacao_municipal.valor DESC
LIMIT 10;

-- Qual é a população total estimada por região?
SELECT
    regioes.nome_regiao,
    SUM(populacao_municipal.valor) AS populacao_total
FROM regioes
JOIN estados
ON regioes.id_regiao = estados.id_regiao
JOIN municipios
ON estados.id_uf = municipios.id_uf
JOIN populacao_municipal
ON municipios.id_municipio = populacao_municipal.id_municipio
GROUP BY regioes.nome_regiao
ORDER BY populacao_total DESC;

-- Qual região concentra a maior população estimada?
SELECT
    regioes.nome_regiao,
    SUM(populacao_municipal.valor) AS populacao_total
FROM regioes
JOIN estados
ON regioes.id_regiao = estados.id_regiao
JOIN municipios
ON estados.id_uf = municipios.id_uf
JOIN populacao_municipal
ON municipios.id_municipio = populacao_municipal.id_municipio
GROUP BY regioes.nome_regiao
ORDER BY populacao_total DESC
LIMIT 1;

-- Quais são os municípios mais populosos do estado do Rio de Janeiro (TOP 10)?
SELECT
    municipios.nome_municipio,
    populacao_municipal.valor AS populacao
FROM populacao_municipal
JOIN municipios
ON populacao_municipal.id_municipio = municipios.id_municipio
JOIN estados
ON municipios.id_uf = estados.id_uf
WHERE estados.sigla_uf = 'RJ'
ORDER BY populacao_municipal.valor DESC
LIMIT 10;

-- Qual é a população média dos municípios por estado?
SELECT
    estados.nome_uf,
    AVG(populacao_municipal.valor) AS media_populacao
FROM estados
JOIN municipios
ON estados.id_uf = municipios.id_uf
JOIN populacao_municipal
ON municipios.id_municipio = populacao_municipal.id_municipio
GROUP BY estados.nome_uf
ORDER BY media_populacao DESC;
