-- analytics.sql

-- 1. Quais são os 10 municípios mais populosos da base?
SELECT m.nome_municipio, pm.valor
FROM municipios m 
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
ORDER BY pm.valor DESC
LIMIT 10;

--Ordenei o select em ordem decrescente de número de pessoas nos municipios e limitei em 10 como solicitado na questão.

-- 2. Quais são os municípios mais populosos de uma UF escolhida?
SELECT m.nome_municipio, e.id_uf, pm.valor
FROM municipios m 
JOIN estados e ON m.id_uf = e.id_uf 
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
WHERE e.id_uf = 33 -- Rio de Janeiro
ORDER BY pm.valor DESC
LIMIT 20;

--A partir do id_uf que identifica uma Unidade Federativa, pegamos os numeros de pessoas em cada municicpio pertencente a essa UF e ordenamos em ordem decrescente, 
-- limitei em 20 para mostrar os top 20 mais populosos. Podemos testar outros UFs trocando a condição do WHERE. 


-- 3. Qual é a população total estimada por região?
SELECT SUM(pm.valor) as populacao_estimada, r.nome_regiao
FROM populacao_municipal pm 
JOIN municipios m ON m.id_municipio = pm.id_municipio 
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
GROUP BY r.nome_regiao 
ORDER BY populacao_estimada DESC;

--A consulta relaciona os municípios aos estados e às regiões, soma a população dos municípios de cada região com SUM e GROUP BY
-- e organiza o resultado em ordem decrescente.

-- 4. Qual é a população média dos municípios por estado?
SELECT ROUND(AVG(pm.valor), 2) as populacao_media, e.nome_uf
FROM populacao_municipal pm 
JOIN municipios m ON pm.id_municipio = m.id_municipio
JOIN estados e ON e.id_uf = m.id_uf 
GROUP BY e.nome_uf, e.id_uf  
ORDER BY populacao_media DESC;

-- A consulta calcula a população média dos municípios de cada estado e ordena os resultados da maior para a menor média.
--O estado com maior população média dos municipios é o Distrito Federal, isso ocorre porque DF só tem um unico municipio, que engloba a capital Brasília.

-- 5. Quais municípios possuem população acima da média nacional?

SELECT m.nome_municipio, pm.valor
FROM populacao_municipal pm
JOIN municipios m ON pm.id_municipio = m.id_municipio
WHERE pm.valor > (SELECT ROUND(AVG(pm.valor), 2) as populacao_media
	FROM populacao_municipal pm) 
;
--A subconsulta calcula a média populacional dos municípios da base. A condição do WHERE mantém apenas os municípios cuja população
--está acima da média.





