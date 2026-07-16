-- analytics.sql
--1. Quais são os municípios mais populosos da base?
SELECT nome_municipio, SUM(valor) AS "Populacao_estimada"
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio)
WHERE indicador == 'populacao_residente_estimada'
GROUP BY nome_municipio
ORDER BY Populacao_estimada DESC;

--2. Quais são os municípios mais populosos de uma UF escolhida?
SELECT nome_municipio, SUM(valor) AS "Populacao_estimada"
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio) INNER JOIN estados
USING (id_uf)
WHERE indicador == 'populacao_residente_estimada'
AND nome_uf == 'Rio de Janeiro'
GROUP BY nome_municipio
ORDER BY Populacao_estimada DESC;

--3. Qual é a população total estimada por região?
SELECT nome_regiao, SUM(valor) AS "Populacao_estimada"
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio) INNER JOIN estados
USING(id_uf) INNER JOIN regioes USING (id_regiao)
WHERE indicador == 'populacao_residente_estimada'
GROUP BY nome_regiao ORDER BY Populacao_estimada DESC;

--4. Qual é a população média dos municípios por estado?
SELECT nome_uf, AVG(valor) AS "Populacao_estimada"
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio) INNER JOIN estados
USING(id_uf)
WHERE indicador == 'populacao_residente_estimada'
GROUP BY nome_uf
ORDER BY Populacao_estimada DESC;

--5. Quais municípios possuem população acima da média nacional dos municípios?
SELECT nome_municipio, valor AS "Populacao_estimada"
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio)
WHERE valor > (
SELECT AVG(valor)
FROM populacao_municipal
WHERE indicador == 'populacao_residente_estimada')
AND indicador == 'populacao_residente_estimada'
ORDER BY Populacao_estimada DESC;