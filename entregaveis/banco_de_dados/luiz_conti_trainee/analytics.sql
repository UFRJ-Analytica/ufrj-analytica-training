-- analytics.sql

--1. Quais são os municípios mais populosos da base?
 
--Ranking 10 municípios mais populosos:
--1.São Paulo	11904961
--2.Rio de Janeiro	6730729
--3.Brasília	2996899
--4.Fortaleza	2578483
--5.Salvador	2564204
--6.Belo Horizonte	2415872
--7.Manaus	2303732
--8.Curitiba	1830795
--9.Recife	1588376
--10.Goiânia	1503256

--Podemos ver que todos os municípios no top 10 são capitais.
 
SELECT nome_municipio, valor
	FROM municipios
	INNER JOIN fato_indicador_municipal
		ON fato_indicador_municipal.id_municipio = municipios.id_municipio
	ORDER BY valor DESC
	LIMIT 10;
 
 
--2. Quais são os municípios mais populosos de uma UF escolhida?

--Ranking 10 municípios mais populosos de São Paulo:
--1.São Paulo	11904961
--2.Guarulhos	1349100.0
--3.Campinas	1187974.0
--4.São Bernardo do Campo	841154.0
--5.Santo André	782048.0
--6.Sorocaba	762172.0
--7.Osasco	759524.0
--8.Ribeirão Preto	731639.0
--9.São José dos Campos	727078.0
--10.São José do Rio Preto	504166.0

--Vemos que o município mais populoso de São Paulo é de fato sua capital.

SELECT nome_municipio, valor
	FROM municipios
	INNER JOIN fato_indicador_municipal
		ON fato_indicador_municipal.id_municipio = municipios.id_municipio
	WHERE municipios.id_uf = 35
	ORDER BY valor DESC
	LIMIT 10;
 
 
--3. Qual é a população total estimada por região?

--Resposta:
--Norte	18.801.282
--Nordeste	57.244.485
--Sudeste	88.825.643
--Sul	31.310.809
--Centro-Oeste	17.232.941

--A partir desses dados, podemos perceber que o estado com maior população total é o Sudeste, apesar de ter apenas 4 estados
--mostrando que a quantidade de estados não é um fator determinante para a população total.
 
SELECT nome_regiao, SUM(valor)
	FROM regioes
	INNER JOIN estados
		ON estados.id_regiao = regioes.id_regiao
	INNER JOIN municipios
		ON municipios.id_uf = estados.id_uf
	INNER JOIN fato_indicador_municipal
		ON fato_indicador_municipal.id_municipio = municipios.id_municipio
	GROUP BY regioes.id_regiao;
 
 
--4. Qual é o estado com a maior população média dos municípios por estado?

--Ranking (top 10):
--1.Distrito Federal	2996899.0
--2.Rio de Janeiro	187212.46739130435
--3.São Paulo	71444.6527131783
--4.Amazonas	69703.48387096774
--5.Pará	60494.416666666664
--6.Espírito Santo	52908.38461538462
--7.Pernambuco	51686.524324324324
--8.Amapá	50407.3125
--9.Ceará	50374.108695652176
--10.Roraima	49251.46666666667

--Vendo o ranking, podemos notar a presença principal de estados pertencentes
--às regiões Sudeste (Rio de Janeiro, São Paulo, Espírito Santo), Norte (Pará, Amapá, Amazonas, Roraima) e Nordetes (Pernambuco e Roraima).
--Apesar do Distrito Federal aparecer em primeiro, é válido esclarecer que, como DF não considera suas regiões administrativas como municípios,
--sua população está presente na database como parte de um unico "município", o que explica sua posição no ranking.
 
SELECT nome_uf, AVG(valor) as media
	FROM estados
	INNER JOIN municipios
		ON municipios.id_uf = estados.id_uf
	INNER JOIN fato_indicador_municipal
		ON fato_indicador_municipal.id_municipio = municipios.id_municipio
	GROUP BY estados.id_uf
	ORDER BY media DESC
	LIMIT 10;


--5. Qual região possui mais municípios com população acima da média nacional?
--Resposta: A partir do ranking criado, podemos ver que o Sudeste é a região com mais municípios acima da média nacional de municípios.
--Ranking:
--Sudeste	333
--Nordeste	268
--Sul	146
--Norte	94
--Centro-Oeste	61

SELECT nome_regiao, COUNT(fato_indicador_municipal.id_municipio) as qtd 
	FROM municipios
	INNER JOIN fato_indicador_municipal
		ON municipios.id_municipio = fato_indicador_municipal.id_municipio
	INNER JOIN estados
		ON municipios.id_uf = estados.id_uf
	INNER JOIN regioes
		ON estados.id_regiao = regioes.id_regiao
	WHERE valor > (SELECT AVG(valor) FROM fato_indicador_municipal)
	GROUP BY regioes.id_regiao
	ORDER BY qtd DESC;




