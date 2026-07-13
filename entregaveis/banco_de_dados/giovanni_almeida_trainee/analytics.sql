-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

--Pergunta 1: Quais municípios possuem população acima da média nacional dos municípios?
SELECT m.nome_municipio, pm.valor as Populacao, 
		(SELECT AVG(pm_sub_select.valor) 
        FROM populacao_municipal pm_sub_select 
        WHERE pm_sub_select.ano = 2025) AS media_geral
FROM municipios m 
	INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
WHERE pm.ano = 2025 
  AND pm.valor > (
      SELECT AVG(pm2.valor)
      FROM populacao_municipal pm2
      WHERE pm2.ano = 2025
  )
GROUP BY m.id_municipio, m.nome_municipio;
--Municípios com população acima da média



--Pergunta 2:Quais estados possuem maior concentração populacional?
SELECT e.nome_uf,
       COUNT(m.id_municipio) AS quantidade_municipios,
       SUM(pm.valor) AS populacao_total,
       AVG(pm.valor) AS concentracao_media_por_municipio
FROM estados e 
INNER JOIN municipios m ON e.id_uf = m.id_uf 
INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
WHERE pm.ano = 2025
GROUP BY e.id_uf, e.nome_uf
ORDER BY concentracao_media_por_municipio DESC
LIMIT 5;
-- Estados com mais população por município, DF é interessante.



--Pergunta 3:Quantos municípios pequenos, médios e grandes existem na base?
WITH EstatisticasGlobais AS (
    SELECT MIN(valor) AS min_populacao,
           AVG(valor) AS avg_populacao,
           MAX(valor) AS max_populacao
    FROM populacao_municipal
    WHERE ano = 2025
),
ClassificacaoMunicipios AS (
    -- Uso A média e o valor máximo para estabelecer os cortes
    SELECT pm.id_municipio,
           CASE 
               WHEN pm.valor < (eg.avg_populacao + eg.min_populacao) / 2.0 
                    THEN 'Pequeno'
               WHEN pm.valor > (eg.avg_populacao + eg.min_populacao) / 2.0 AND pm.valor < (eg.avg_populacao + eg.max_populacao) / 2.0
					THEN 'Médio'
               ELSE 'Grande'
           END AS categoria_tamanho
    FROM populacao_municipal pm
    --Cross join para todos os municípios terem a informação da média, min e max
    CROSS JOIN EstatisticasGlobais eg
    WHERE pm.ano = 2025
)
-- Contagem por categoria
SELECT categoria_tamanho,
       COUNT(id_municipio) AS total_municipios
FROM ClassificacaoMunicipios
GROUP BY categoria_tamanho
ORDER BY total_municipios DESC;

--Defini o grande, médio e pequeno com base no meu critério e contei a quantidade de municípios que se encaixam com o estabelecido
--O resultado acabou revelando que há poucos municípios MUITO outliers, que puxam o MAX para o alto demais,
--e acabam levando ao resultado de apenas 2 municípios grandes. De curiosidade, são esses:
WITH EstatisticasGlobais AS (
    SELECT MIN(valor) AS min_populacao,
           AVG(valor) AS avg_populacao,
           MAX(valor) AS max_populacao
    FROM populacao_municipal
    WHERE ano = 2025
),
ClassificacaoMunicipios AS (
    -- Uso A média e o valor máximo para estabelecer os cortes
    SELECT pm.id_municipio,
           CASE 
               WHEN pm.valor < (eg.avg_populacao + eg.min_populacao) / 2.0 
                    THEN 'Pequeno'
               WHEN pm.valor > (eg.avg_populacao + eg.min_populacao) / 2.0 AND pm.valor < (eg.avg_populacao + eg.max_populacao) / 2.0
					THEN 'Médio'
               ELSE 'Grande'
           END AS categoria_tamanho
    FROM populacao_municipal pm
    --Cross join para todos os municípios terem a informação da média, min e max
    CROSS JOIN EstatisticasGlobais eg
    WHERE pm.ano = 2025
)
--Nome
SELECT m.nome_municipio, 
       c.categoria_tamanho,
       pm.valor
FROM ClassificacaoMunicipios c
INNER JOIN municipios m ON c.id_municipio = m.id_municipio
INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
WHERE c.categoria_tamanho = 'Grande';



--Pergunta 4:Quais regiões possuem maior relação população/número de municípios
SELECT r.nome_regiao,
       SUM(pm.valor) AS populacao_total,
       COUNT(m.id_municipio) AS total_municipios,
       CAST(SUM(pm.valor) AS INTEGER) / COUNT(m.id_municipio) AS relacao_populacao_municipio
FROM regioes r
INNER JOIN estados e ON r.id_regiao = e.id_regiao
INNER JOIN municipios m ON e.id_uf = m.id_uf
INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
WHERE pm.ano = 2025
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY relacao_populacao_municipio DESC;
--Para saber qual região tem os municípios mais "gordos"





--Pergunta 5:Quais os municípios mais populosos do Rio de Janeiro
SELECT m.nome_municipio,
       pm.valor AS populacao
FROM estados e
INNER JOIN municipios m ON e.id_uf = m.id_uf
INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
WHERE e.nome_uf = 'Rio de Janeiro' 
  AND pm.ano = 2025
ORDER BY populacao DESC
LIMIT 10;
--Pergunta simples: pra matar uma curiosidade que eu tenho em relação ao RJ