-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.
PRAGMA foreign_keys = ON;

--1.Quais são os municípios mais populosos da base?
SELECT 
	m.nome_municipio,
	e.sigla_uf,
	f.valor AS populacao
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio 
JOIN estados e ON e.id_uf  = m.id_uf 
JOIN indicadores i ON i.id_indicador = f.id_indicador 
WHERE i.nome_indicador  = 'populacao_residente_estimada'
ORDER BY f.valor DESC
LIMIT 10;
-- Os municipios de São Paulo e Rio no topo evidenciada pela sua importancia global no país, seguida da capital do país e outros municipios que possuem importancia histórica.

--2.Quais são os municípios mais populosos de uma UF escolhida?
SELECT 
	m.nome_municipio,
	f.valor AS populacao
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio  = f.id_municipio 
JOIN estados e ON e.id_uf  = m.id_uf 
JOIN indicadores i ON i.id_indicador = f.id_indicador 
WHERE i.nome_indicador = 'populacao_residente_estimada'
	AND e.sigla_uf  = 'RJ'
ORDER BY f.valor DESC
LIMIT 10;
-- Podemos perceber que a capital do Rio é a mais populosa, mostrando sua forte concentração populacional em relação aos outros municipios do estado

--3.Qual é a população total estimada por região?
SELECT 
	r.nome_regiao,
	SUM(f.valor) AS populacao_total
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio 
JOIN estados e ON e.id_uf = m.id_uf 
JOIN regioes r ON r.id_regiao = e.id_regiao 
JOIN indicadores i ON i.id_indicador = f.id_indicador 
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY r.id_regiao , r.nome_regiao 
ORDER BY populacao_total DESC;
-- Analisando percebemos que a regiao sudeste é a regiao com maior populacao total e a regiao Centro-Oeste, podendo ser explicada por sua ocupação tardia

--4.Qual é a população média dos municípios por estado? 
SELECT
    e.sigla_uf,
    e.nome_uf,
    ROUND(AVG(f.valor), 2) AS populacao_media
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN indicadores i ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_media DESC;
-- Podemos notar que DF aparece no topo porque ele é tratado como um unico "municipio" o que faz com que a media seja divida por 1 municipio, deixando essa media muito alta. quando comparado com outros estados que possuem diversos municipios

--5.Qual região concentra a maior população estimada? 
SELECT
    r.nome_regiao,
    SUM(f.valor) AS populacao_total
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
JOIN indicadores i ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total DESC
LIMIT 1;
-- Atraves da consulta podemos ver que a regiao Sudeste é a regiao que concentra a maior parte da populacao do país