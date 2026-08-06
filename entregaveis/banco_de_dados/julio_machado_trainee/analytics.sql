-- 1. Qual é a população média dos municípios por estado?

SELECT
	nome_uf AS Estado,
	ROUND(AVG(valor),2) AS populacao_media
FROM municipios m 
INNER JOIN estados e 
	ON m.id_uf = e.id_uf 
INNER JOIN recenseamento r 
	ON m.id_municipio = r.id_municipio
WHERE r.id_censo = 1
GROUP BY Estado
ORDER BY populacao_media DESC;

-- 2. Quantos municípios pequenos, médios e grandes existem na base?
-- PEQUENO < 100000 / MÉDIO 100000 ATÉ 499999 / GRANDE >= 500000

SELECT
	COUNT(valor) FILTER(WHERE valor >= 500000) AS GRANDE,
	COUNT(CASE WHEN valor >= 100000 AND valor < 500000 THEN 1 END) AS MEDIO,
	SUM(IF(valor < 100000, 1, 0)) AS PEQUENO
FROM municipios m 
INNER JOIN recenseamento r 
	ON m.id_municipio = r.id_municipio AND r.id_censo = 1;

-- 3. Qual região concentra a maior população estimada?

SELECT
	nome_regiao,
	SUM(valor) AS populacao
FROM municipios m 
INNER JOIN estados e 
	ON m.id_uf = e.id_uf 
INNER JOIN regioes r 
	ON e.id_regiao = r.id_regiao 
INNER JOIN recenseamento r2 
	ON m.id_municipio  = r2.id_municipio AND r2.id_censo = 1
GROUP BY nome_regiao
ORDER BY populacao DESC
LIMIT 1;

-- 4. 5 Municípios mais populosos?

SELECT
	nome_municipio AS Municipio,
	valor as Populacao
FROM municipios m 
INNER JOIN recenseamento r 
	ON m.id_municipio  = r.id_municipio AND r.id_censo =1
ORDER BY Populacao DESC
LIMIT 5;

-- 5. Quantos municipios grandes existem por Estado?

SELECT
	nome_uf AS Estado,
	COUNT(valor) FILTER(WHERE valor >= 500000) AS Municipio_Grande
FROM municipios m
INNER JOIN estados e 
	ON m.id_uf = e.id_uf 
INNER JOIN recenseamento r 
	ON m.id_municipio = r.id_municipio AND r.id_censo = 1
GROUP BY Estado
ORDER BY Municipio_Grande DESC;
