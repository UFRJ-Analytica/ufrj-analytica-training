-- analytics.sql
-- Consultas analiticas sobre o modelo normalizado: ranking, distribuicao,
-- classificacao e concentracao da populacao estimada por municipio,
-- estado e regiao.

PRAGMA foreign_keys = ON;

-- 1. Quais sao os municipios mais populosos da base? (ranking nacional, Top 15)
SELECT
    m.nome_municipio,
    e.sigla_uf,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
ORDER BY f.valor DESC
LIMIT 15;


-- 2. Quais sao os municipios mais populosos de uma UF escolhida? (exemplo: SP)
SELECT
    m.nome_municipio,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
WHERE e.sigla_uf = 'SP'
ORDER BY f.valor DESC
LIMIT 10;


-- 3. Qual e a populacao total estimada por regiao, e qual o percentual
--    que cada regiao representa da populacao nacional?
SELECT
    r.nome_regiao,
    SUM(f.valor) AS populacao_total,
    ROUND(
        100.0 * SUM(f.valor) / (SELECT SUM(valor) FROM fato_indicador_municipal),
        2
    ) AS percentual_do_brasil
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total DESC;


-- 4. Qual e a populacao media dos municipios por estado?
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios,
    ROUND(AVG(f.valor), 0) AS populacao_media_municipio
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_media_municipio DESC;


-- 5. Quais municipios possuem populacao acima da media nacional dos municipios?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
WHERE f.valor > (SELECT AVG(valor) FROM fato_indicador_municipal)
ORDER BY f.valor DESC;


-- 6. Quantos municipios pequenos, medios e grandes existem na base?
-- Faixas de porte: pequeno < 20 mil hab., medio 20 mil-100 mil, grande >= 100 mil.
SELECT
    CASE
        WHEN f.valor < 20000 THEN 'Pequeno (< 20 mil hab.)'
        WHEN f.valor < 100000 THEN 'Medio (20 mil a 100 mil hab.)'
        ELSE 'Grande (>= 100 mil hab.)'
    END AS porte_municipio,
    COUNT(*) AS qtd_municipios
FROM fato_indicador_municipal f
GROUP BY porte_municipio
ORDER BY qtd_municipios DESC;


-- 7. Quantos municipios pequenos, medios e grandes existem por regiao?
SELECT
    r.nome_regiao,
    CASE
        WHEN f.valor < 20000 THEN 'Pequeno (< 20 mil hab.)'
        WHEN f.valor < 100000 THEN 'Medio (20 mil a 100 mil hab.)'
        ELSE 'Grande (>= 100 mil hab.)'
    END AS porte_municipio,
    COUNT(*) AS qtd_municipios
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.nome_regiao, porte_municipio
ORDER BY r.nome_regiao, qtd_municipios DESC;


-- 8. Quais estados possuem maior concentracao populacional em poucos
--    municipios? (percentual da populacao do estado que esta nos 3
--    municipios mais populosos daquele estado)
WITH ranking_uf AS (
    SELECT
        e.id_uf,
        f.valor,
        ROW_NUMBER() OVER (
            PARTITION BY e.id_uf ORDER BY f.valor DESC
        ) AS posicao_no_estado
    FROM fato_indicador_municipal f
    JOIN municipios m ON m.id_municipio = f.id_municipio
    JOIN estados e ON e.id_uf = m.id_uf
),
resumo_uf AS (
    SELECT
        id_uf,
        SUM(valor) AS populacao_total_estado,
        SUM(CASE WHEN posicao_no_estado <= 3 THEN valor ELSE 0 END) AS populacao_top3_municipios
    FROM ranking_uf
    GROUP BY id_uf
)
SELECT
    e.sigla_uf,
    e.nome_uf,
    resumo_uf.populacao_total_estado,
    resumo_uf.populacao_top3_municipios,
    ROUND(
        100.0 * resumo_uf.populacao_top3_municipios / resumo_uf.populacao_total_estado,
        2
    ) AS percentual_concentrado_top3
FROM resumo_uf
JOIN estados e ON e.id_uf = resumo_uf.id_uf
ORDER BY percentual_concentrado_top3 DESC
LIMIT 10;
