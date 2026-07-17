-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.

-- 1. View de Resumo Demográfico
DROP VIEW IF EXISTS vw_resumo_demografico;

CREATE VIEW vw_resumo_demografico AS
SELECT
    reg.nome_regiao,
    est.nome_uf,
    est.sigla_uf,
    mun.nome_municipio,
    pop.ano,
    pop.valor_populacao
FROM regioes reg
JOIN estados est ON reg.id_regiao = est.id_regiao
JOIN municipios mun ON est.id_uf = mun.id_uf
JOIN populacao pop ON mun.id_municipio = pop.id_municipio
WHERE pop.ano = (SELECT MAX(ano) FROM populacao); --filtro para sempre escolher o ultimo ano disponivel
-- Como usar a view:
-- SELECT * FROM vw_resumo_demografico WHERE sigla_uf = 'SP'


-- 2. Ranking top 10 municipios mais populosos
SELECT
    mun.nome_municipio,
    est.sigla_uf,
    pop.valor_populacao
FROM vw_resumo_demografico
ORDER BY pop.valor_populacao DESC
LIMIT 10;

-- 3. Os 3 municipios mais populosos de CADA estados
WITH ranking_municipio_por_estado AS( 
    SELECT
        mun.nome_municipio,
        est.sigla_uf,
        pop.valor_populacao,
        RANK() OVER(PARTITION BY est.sigla_uf ORDER BY pop.valor_populacao DESC) AS posicao_no_estado
    FROM vw_resumo_demografico
)
SELECT *
FROM ranking_municipio_por_estado
WHERE posicao_no_estado <= 3
ORDER BY sigla_uf, posicao_no_estado;


-- 4. Concentração populacional
WITH concentracao_populacional AS(
    SELECT
        mun.nome_municipio,
        SUM(pop.valor_populacao) OVER() AS populacao_total_brasil,                                             -- Total do país
        SUM(pop.valor_populacao) OVER(ORDER BY pop.valor_populacao DESC) AS populacao_acumulada -- SUM() OVER() soma cumulativamente
    FROM vw_resumo_demografico
    )
SELECT
    nome_municipio,
    sigla_uf,
    valor_populacao,
    ROUND(100.0 * (populacao_acumulada / populacao_total_brasil), 2) AS pct_acumulado
FROM concentracao_populacional
ORDER BY pct_acumulado DESC;

-- 5. Estados com população superior a 10 Milhões
SELECT 
    est.sigla_uf,
    SUM(pop.valor_populacao) AS populacao_total_estado
FROM vw_resumo_demografico
GROUP BY est.sigla_uf
HAVING SUM(pop.valor_populacao) >= 1000000
ORDER BY populacao_total_estado DESC;

