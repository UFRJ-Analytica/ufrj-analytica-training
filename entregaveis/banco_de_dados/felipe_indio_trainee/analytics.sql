--1. Qual é a população total estimada por região?
SELECT r.nome_regiao, SUM(pm.valor) populacao FROM populacao_municipal pm
JOIN municipios m ON m.id_municipio = pm.id_municipio
JOIN estados e ON e.id_uf  = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.nome_regiao
ORDER BY populacao DESC;

/* Resposta: 
Sudeste: 88.825.634
Nordeste: 57.244.485
Sul: 31.310.809
Norte: 18.801.282
Centro-Oeste: 17.232.941
*/

--2.  Qual é a população média dos municípios por estado?
SELECT e.nome_uf, ROUND(AVG(pm.valor),2) populacao_media FROM populacao_municipal pm  
JOIN municipios m ON m.id_municipio = pm.id_municipio
JOIN estados e ON e.id_uf  = m.id_uf
GROUP BY e.nome_uf
ORDER BY populacao_media DESC;

--A query analisa a distribuição da população dos estados entre os munícpios, logicamente o primeiro lugar é o Distrito Federal, pois ele é apenas um muncípio.

--3. Quais municípios possuem população acima da média nacional dos municípios?
SELECT m.nome_municipio, pm.valor, 
ROUND((SELECT AVG(pm.valor) FROM populacao_municipal pm),2) as media_nacional_dos_municipios  
FROM municipios m
JOIN populacao_municipal pm ON pm.id_municipio = m.id_municipio
WHERE pm.valor > (SELECT AVG(pm.valor) FROM populacao_municipal pm)
ORDER BY pm.valor DESC;

--4. Quais são os municípios mais populosos da base?
SELECT m.nome_municipio, SUM(pm.valor) populacao FROM populacao_municipal pm  
JOIN municipios m ON m.id_municipio = pm.id_municipio
GROUP BY m.nome_municipio 
ORDER BY populacao DESC
LIMIT 10;

-- Os 10 municípios mais populosos são capitais e o distrito federal

--5. Quantos municípios pequenos, médios e grandes existem por região?
WITH separacao_por_quartis AS(
SELECT 
m.id_municipio,
r.id_regiao,
pm.valor,
NTILE(4) OVER (ORDER BY pm.valor ASC) AS quartil
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
JOIN populacao_municipal pm  ON pm.id_municipio = m.id_municipio 
)
SELECT 
r.nome_regiao,
SUM(CASE WHEN q.quartil = 1 THEN 1 ELSE 0 END) AS qtd_pequenos,
SUM(CASE WHEN q.quartil IN (2,3) THEN 1 ELSE 0 END) AS qtd_medios,
SUM(CASE WHEN q.quartil = 4 THEN 1 ELSE 0 END) AS qtd_grandes
FROM separacao_por_quartis q
JOIN regioes r ON r.id_regiao = q.id_regiao
GROUP BY r.nome_regiao;

/*Nessa query eu utilizei uma CTE para calcular os quartis da populaçao e classifiquei os municípios da seguinte forma:
 Pequeno: os municípios presentes no primeiro quartil da população;
 Médio: os municípios presentes no segundo e no terceiro quartil da população;
 Grande: os municípios presentes no quarto quartil da população
*/