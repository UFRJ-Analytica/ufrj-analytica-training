-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- 1. Quais são os municípios mais populosos da base?
SELECT 
	m.nome_municipio,
	SUM(valor) as populacao
FROM municipios m
JOIN fato_indicador_municipal fim 
ON m.id_municipio = fim.id_municipio
GROUP BY m.nome_municipio 
ORDER BY populacao DESC 
LIMIT 10

-- 2. Quais são os municípios mais populosos de uma UF escolhida? 
SELECT 
	m.nome_municipio,
	SUM(valor) as populacao
FROM municipios m
JOIN fato_indicador_municipal fim 
ON m.id_municipio = fim.id_municipio
JOIN estados e 
ON e.id_uf = m.id_uf 
WHERE e.nome_uf = 'Rio de Janeiro'
GROUP BY m.nome_municipio 
ORDER BY populacao DESC 
LIMIT 10;

-- 3. Qual é a população total estimada por região? 
SELECT 
	r.nome_regiao,
	SUM(valor) as populacao
FROM municipios m
JOIN fato_indicador_municipal fim 
ON m.id_municipio = fim.id_municipio
JOIN estados e 
ON e.id_uf = m.id_uf
JOIN regioes r 
ON r.id_regiao = e.id_regiao
GROUP BY r.nome_regiao
ORDER BY populacao DESC 
LIMIT 10;

-- 4. Qual é a população média dos municípios por estado? 
SELECT 
	e.sigla_uf,
	ROUND(AVG(fim.valor),2) AS populacao_media
FROM fato_indicador_municipal fim
JOIN municipios m ON fim.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
GROUP BY e.sigla_uf
ORDER BY populacao_media DESC;

-- 5. Quais municípios possuem população acima da média nacional dos municípios?
SELECT 
	m.nome_municipio, 
	fim.valor, 
	(SELECT AVG(fim.valor)FROM fato_indicador_municipal fim) AS media_nacional
FROM fato_indicador_municipal fim
JOIN municipios m ON fim.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
GROUP BY m.nome_municipio, fim.valor 
HAVING fim.valor > media_nacional
ORDER BY fim.valor ASC;

-- 6. Quantos municípios pequenos, médios e grandes existem na base?
SELECT
	IF (fim.valor > 1000000, "Grande", IF(fim.valor > 200000, "Médio", "Pequeno")) AS classificacao,
	COUNT(m.id_municipio) AS total_municipios
FROM municipios m
JOIN fato_indicador_municipal fim ON m.id_municipio = fim.id_municipio
GROUP BY classificacao;

-- Tambem podemos fazer com IF

SELECT
    CASE 
        WHEN fim.valor > 1000000 THEN 'Grande'
        WHEN fim.valor > 200000 THEN 'Médio'
        ELSE 'Pequeno'
    END AS classificacao,
    COUNT(m.id_municipio) AS total_municipios
FROM municipios m
JOIN fato_indicador_municipal fim ON m.id_municipio = fim.id_municipio
GROUP BY classificacao;


-- 7. Quantos municípios pequenos, médios e grandes existem por região? 
SELECT
	r.nome_regiao,
    CASE 
        WHEN fim.valor > 1000000 THEN 'Grande'
        WHEN fim.valor > 200000 THEN 'Médio'
        ELSE 'Pequeno'
    END AS classificacao,
    COUNT(m.id_municipio) AS total_municipios
FROM municipios m
JOIN fato_indicador_municipal fim ON m.id_municipio = fim.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao  = e.id_regiao
GROUP BY r.nome_regiao, classificacao;

-- 8. Qual região concentra a maior população estimada? 
SELECT 
	r.nome_regiao,
	SUM(valor) as populacao
FROM municipios m
JOIN fato_indicador_municipal fim 
ON m.id_municipio = fim.id_municipio
JOIN estados e 
ON e.id_uf = m.id_uf
JOIN regioes r 
ON r.id_regiao = e.id_regiao
GROUP BY r.nome_regiao
ORDER BY populacao DESC 
LIMIT 1;