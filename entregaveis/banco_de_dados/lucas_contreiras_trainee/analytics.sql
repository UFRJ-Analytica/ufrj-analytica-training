-- analytics.sql
-- Consultas analíticas e camada de análise para exploração de dados de população por município, estado e região
-- Autor: Lucas Contreiras

-- A1: Ranking dos 20 municípios mais populosos
SELECT TOP 20
    ROW_NUMBER() OVER (ORDER BY fi.valor_populacao_estimada DESC) AS ranking,
    m.nome_municipio, 
    e.nome_estado, 
    e.uf, 
    r.nome_regiao,
    fi.valor_populacao_estimada,
    fi.ano_referencia
FROM fato_indicador_municipal fi
JOIN municipios m ON fi.id_municipio = m.id_municipio
JOIN estados e ON m.id_estado = e.id_estado
JOIN regioes r ON e.id_regiao = r.id_regiao
ORDER BY fi.valor_populacao_estimada DESC;

-- A2: Ranking dos 10 estados mais populosos
SELECT TOP 10
    ROW_NUMBER() OVER (ORDER BY SUM(fi.valor_populacao_estimada) DESC) AS ranking,
    e.nome_estado, 
    e.uf, 
    r.nome_regiao,
    SUM(fi.valor_populacao_estimada) AS populacao_total,
    COUNT(DISTINCT m.id_municipio) AS total_municipios,
    ROUND(AVG(fi.valor_populacao_estimada), 2) AS populacao_media_municipal
FROM estados e
JOIN municipios m ON e.id_estado = m.id_estado
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
JOIN regioes r ON e.id_regiao = r.id_regiao
GROUP BY e.id_estado, e.nome_estado, e.uf, r.nome_regiao
ORDER BY populacao_total DESC;

-- A3: Distribuição de população por região (análise agregada)
SELECT 
    r.nome_regiao,
    COUNT(DISTINCT e.id_estado) AS total_estados,
    COUNT(DISTINCT m.id_municipio) AS total_municipios,
    SUM(fi.valor_populacao_estimada) AS populacao_total_regiao,
    ROUND(AVG(fi.valor_populacao_estimada), 2) AS populacao_media_municipal,
    MIN(fi.valor_populacao_estimada) AS populacao_minima,
    MAX(fi.valor_populacao_estimada) AS populacao_maxima,
    ROUND(CAST(SUM(fi.valor_populacao_estimada) AS FLOAT) / 
        (SELECT SUM(valor_populacao_estimada) FROM fato_indicador_municipal) * 100, 2) AS percentual_populacao_nacional
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_estado = m.id_estado
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total_regiao DESC;

-- A4: Classificação de municípios por tamanho de população
SELECT 
    m.nome_municipio,
    e.nome_estado,
    e.uf,
    r.nome_regiao,
    fi.valor_populacao_estimada,
    CASE 
        WHEN fi.valor_populacao_estimada >= 1000000 THEN 'Metrópole (≥1M)'
        WHEN fi.valor_populacao_estimada >= 100000 THEN 'Grande (100K-1M)'
        WHEN fi.valor_populacao_estimada >= 50000 THEN 'Médio (50K-100K)'
        WHEN fi.valor_populacao_estimada >= 20000 THEN 'Pequeno (20K-50K)'
        ELSE 'Muito Pequeno (<20K)'
    END AS categoria_tamanho
FROM fato_indicador_municipal fi
JOIN municipios m ON fi.id_municipio = m.id_municipio
JOIN estados e ON m.id_estado = e.id_estado
JOIN regioes r ON e.id_regiao = r.id_regiao
ORDER BY fi.valor_populacao_estimada DESC;

-- A5: Municípios acima da média de população por estado
WITH media_por_estado AS (
    SELECT 
        e.id_estado,
        e.nome_estado,
        AVG(fi.valor_populacao_estimada) AS media_estado
    FROM estados e
    JOIN municipios m ON e.id_estado = m.id_estado
    LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
    GROUP BY e.id_estado, e.nome_estado
)
SELECT 
    mpe.nome_estado,
    e.uf,
    m.nome_municipio,
    fi.valor_populacao_estimada,
    ROUND(fi.valor_populacao_estimada - mpe.media_estado, 2) AS diferenca_media,
    ROUND((fi.valor_populacao_estimada / mpe.media_estado - 1) * 100, 2) AS percentual_acima_media
FROM media_por_estado mpe
JOIN estados e ON mpe.id_estado = e.id_estado
JOIN municipios m ON e.id_estado = m.id_estado
JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
WHERE fi.valor_populacao_estimada > mpe.media_estado
ORDER BY mpe.nome_estado, fi.valor_populacao_estimada DESC;

-- A6: Concentração de população - Regra de Pareto por região
WITH populacao_ranqueada AS (
    SELECT 
        r.id_regiao,
        r.nome_regiao,
        m.nome_municipio,
        e.nome_estado,
        fi.valor_populacao_estimada,
        ROW_NUMBER() OVER (PARTITION BY r.id_regiao ORDER BY fi.valor_populacao_estimada DESC) AS ranking_regiao,
        SUM(fi.valor_populacao_estimada) OVER (PARTITION BY r.id_regiao) AS populacao_total_regiao
    FROM regioes r
    JOIN estados e ON r.id_regiao = e.id_regiao
    JOIN municipios m ON e.id_estado = m.id_estado
    JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
)
SELECT 
    nome_regiao,
    COUNT(*) AS total_municipios_para_80_pct,
    SUM(valor_populacao_estimada) AS populacao_concentrada,
    ROUND(CAST(SUM(valor_populacao_estimada) AS FLOAT) / 
        (SELECT MAX(populacao_total_regiao) FROM populacao_ranqueada WHERE nome_regiao = populacao_ranqueada.nome_regiao) * 100, 2) AS percentual_concentracao
FROM populacao_ranqueada
WHERE valor_populacao_estimada * 100.0 / populacao_total_regiao <= 80
GROUP BY nome_regiao
ORDER BY percentual_concentracao DESC;
