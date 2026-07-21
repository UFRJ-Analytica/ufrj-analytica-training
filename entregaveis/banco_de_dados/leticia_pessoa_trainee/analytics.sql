-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.

-- ==============================
-- VIEW DE BASE PARA AS ANALISES
-- ==============================
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


-- 1. Quais são os municipios mais populosos da base? (Top 10)
SELECT
    nome_municipio,
    sigla_uf,
    valor_populacao
FROM vw_resumo_demografico
ORDER BY valor_populacao DESC
LIMIT 10;

-- 2. Quais os municipios mais populosos de uma UF escolhida? (TOP 3 por uf)
WITH ranking_municipio_por_estado AS( 
    SELECT
        nome_municipio,
        sigla_uf,
        valor_populacao,
        RANK() OVER(PARTITION BY sigla_uf ORDER BY valor_populacao DESC) AS posicao_no_estado
    FROM vw_resumo_demografico
)
SELECT *
FROM ranking_municipio_por_estado
WHERE posicao_no_estado <= 3
ORDER BY sigla_uf, posicao_no_estado;


-- 3. Quais estados possuem maior concentração populacional em poucos municipios
WITH concentracao_populacional AS(
    SELECT
        nome_municipio,
        sigla_uf,
        valor_populacao,
        SUM(valor_populacao) OVER() AS populacao_total_brasil,                                             -- Total do país
        SUM(valor_populacao) OVER(ORDER BY valor_populacao DESC) AS populacao_acumulada -- SUM() OVER() soma cumulativamente
    FROM vw_resumo_demografico
    )
SELECT
    nome_municipio,
    sigla_uf,
    valor_populacao,
    ROUND(100.0 * (populacao_acumulada / populacao_total_brasil), 2) AS pct_acumulado
FROM concentracao_populacional
ORDER BY pct_acumulado DESC;

-- 4. Quais estados concentram uma população superior a 10 Milhões?
SELECT 
    sigla_uf,
    SUM(valor_populacao) AS populacao_total_estado
FROM vw_resumo_demografico
GROUP BY sigla_uf
HAVING SUM(valor_populacao) >= 10000000
ORDER BY populacao_total_estado DESC;

-- 5. Qual é a população total estimada por região?
SELECT 
    nome_regiao,
    SUM(valor_populacao) AS populacao_regional
FROM vw_resumo_demografico
GROUP BY nome_regiao
ORDER BY populacao_regional DESC;

-- 6. Qual é a média dos municípios por estado?
SELECT
    sigla_uf,
    ROUND(AVG(valor_populacao), 0) AS media_habitantes_por_municipio
FROM vw_resumo_demografico
GROUP BY sigla_uf, nome_uf
ORDER BY media_habitantes_por_municipio DESC;

-- 7. Quais municipios possuem população acima da média nacional dos municipios
SELECT
    nome_municipio,
    sigla_uf,
    valor_populacao
FROM vw_resumo_demografico
WHERE valor_populacao >(SELECT AVG(valor_populacao) FROM vw_resumo_demografico)
ORDER BY valor_populacao DESC;

-- 8. Quantos municipios pequenos, medios e grandes existem na base
SELECT 
    CASE
        WHEN valor_populacao <= 20000 THEN '1. Pequeno'
        WHEN valor_populacao <= 100000 THEN '2. Médio'
        WHEN valor_populacao <= 500000 THEN '3. Grande'
        ELSE '4. Metrópole'
    END AS porte_populacional,
    COUNT(*) AS quantidade_municipios,
    SUM(valor_populacao) AS populacao_total_porte
FROM vw_resumo_demografico
GROUP BY porte_populacional
ORDER BY porte_populacional;
