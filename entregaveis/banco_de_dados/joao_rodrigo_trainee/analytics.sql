-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- Vou responder uma pergunta de cada eixo descrito na entrega:
-- Comparação, ranking, distribuição, classificação e síntese dos dados.

------------------------------------------------------------------------------------------

-- Comparação: Quais municípios possuem população acima da média nacional dos municípios?
-- 
-- Aqui foi necessário apenas um join, com a tabela de população municipal.

SELECT 
    m.nome_municipio, 
    pm.valor 
FROM municipios m
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
WHERE pm.valor > (
    SELECT AVG(pm2.valor)
    FROM populacao_municipal pm2
);

-- Ranking: Quais são os municípios mais populosos de uma UF escolhida?
-- 
-- Escolhi fazer o top 10 do estado do Rio de Janeiro

SELECT m.nome_municipio, pm.valor
FROM municipios m
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
JOIN estados e ON m.id_uf = e.id_uf 
WHERE e.nome_uf = 'Rio de Janeiro'
ORDER BY pm.valor DESC
LIMIT 10;

-- Distribuição: Quais estados possuem maior concentração populacional em poucos municípios?
--
-- Nesse caso, abordei o problema somando a população dos 5 municípios mais populosos de 
-- 		cada estado e, em seguida, dividindo pela população total daquele estado.
-- O Distrito Federal não possui municípios, então foi desconsiderado.
-- Como o enunciado não pediu um ranking, limitei a resposta apenas aos 5 estados com maior 
-- 		índice.

SELECT 
	e.nome_uf,
	(
        SELECT SUM(valor) 
        FROM (
            SELECT pm2.valor 
            FROM populacao_municipal pm2 
            JOIN municipios m2 ON pm2.id_municipio = m2.id_municipio 
            WHERE m2.id_uf = e.id_uf 
            ORDER BY pm2.valor DESC 
            LIMIT 5
        )
    ) / SUM(pm.valor) AS indice
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf 
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
WHERE e.nome_uf != 'Distrito Federal'
GROUP BY e.id_uf, e.nome_uf 
ORDER BY indice DESC
LIMIT 5;

-- Classificação: Quantos municípios pequenos, médios e grandes existem na base?
--
-- Classifiquei de forma arbitrária, com municípios pequenos sendo os que possuem população 
-- 		menor que 100 mil, os médios, entre 100 mil e 500 mil (inclusos), e os grandes, acima de 
-- 		500 mil.

SELECT 
	CASE 
		WHEN pm.valor < 100000 THEN 'Pequeno'
		WHEN pm.valor BETWEEN 100000 AND 500000 THEN 'Médio'
		ELSE 'Grande'
	END AS tamanho, 
	COUNT(m.id_municipio) AS quantidade
FROM municipios m 
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
GROUP BY tamanho
ORDER BY quantidade DESC;

-- Síntese dos dados: Qual é a população média dos municípios por estado?
-- 
-- Aqui, eu agreguei por estado e calculei a média, com join nas tabelas
-- 		de municípios e população municipal

SELECT 
	e.nome_uf, 
	AVG(pm.valor) AS media_populacional
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf 
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
GROUP BY e.id_uf, e.nome_uf;
