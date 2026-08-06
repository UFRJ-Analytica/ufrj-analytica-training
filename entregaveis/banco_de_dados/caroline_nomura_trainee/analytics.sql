-- 1. Quais são os municípios mais populosos da base?
SELECT 
    m.nome_municipio, 
    e.sigla_uf, 
    p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
ORDER BY p.valor DESC;
-- O município mais populoso é São Paulo, tendo quase o dobro da população do Rio de Janeiro que está em segundo lugar, e em terceiro lugar temos Brasília.

-- 2. Qual é a população média dos municípios por estado?
SELECT 
    e.nome_uf, 
    ROUND(AVG(p.valor), 2) AS media_populacional_municipio
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
GROUP BY e.nome_uf
ORDER BY media_populacional_municipio DESC;
-- O Distrito Federal lidera com uma média de quase 3 milhões (pois conta como município único), o Rio de Janeiro vem em segundo lugar, tendo mais que o dobro da média de São Paulo, que ocupa o terceiro lugar.

-- 3. Qual região concentra a maior população estimada?
SELECT 
    r.nome_regiao, 
    SUM(p.valor) AS populacao_total_regiao
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
GROUP BY r.nome_regiao
ORDER BY populacao_total_regiao DESC;
-- A região Sudeste concentra a maior parte da população do país com quase 89 milhões de habitantes, superando o Nordeste, que fica em segundo lugar. O Centro-Oeste possui a menor população total.

-- 4. Quantos municípios pequenos, médios e grandes existem na base?
SELECT 
    CASE 
        WHEN valor < 50000 THEN 'Pequeno (<50k)'
        WHEN valor >= 50000 AND valor <= 100000 THEN 'Médio (50k a 100k)'
        ELSE 'Grande (>100k)' 
    END AS porte_municipio,
    COUNT(id_municipio) AS quantidade_municipios
FROM populacao_municipal
GROUP BY porte_municipio
ORDER BY quantidade_municipios DESC;
-- A maioria dos municípios é de pequeno porte (com menos de 50 mil habitantes segundo a classificação do IBGE), totalizando 4.888 cidades. Em contraste, o número de municípios médios e grandes representa uma pequena minoria.

-- 5. Quais são os municípios mais populosos de uma UF escolhida (RJ)?
SELECT 
    m.nome_municipio, 
    p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
WHERE e.sigla_uf = 'RJ' 
ORDER BY p.valor DESC;
-- A capital lidera disparado o ranking, sendo seguida por outros grandes centros urbanos do estado, como São Gonçalo, Duque de Caxias e Nova Iguaçu, que tem tamanhos de população parecidos.