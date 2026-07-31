-- analytics.sql
-- Consultas analíticas e camada de análise para exploração de dados de população por município, estado e região
-- Autor: Lucas Contreiras

-- A1: Ranking dos 20 municípios mais populosos
SELECT
    ROW_NUMBER() OVER (ORDER BY fi.valor DESC) AS ranking,
    m.nome_municipio, 
    e.nome_uf, 
    e.sigla_uf, 
    r.nome_regiao,
    fi.valor,
    fi.ano
FROM fato_indicador_municipal fi
JOIN municipios m ON fi.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
ORDER BY fi.valor DESC
LIMIT 20;

-- A2: Ranking dos 10 estados mais populosos
SELECT
    ROW_NUMBER() OVER (ORDER BY SUM(fi.valor) DESC) AS ranking,
    e.nome_uf, 
    e.sigla_uf, 
    r.nome_regiao,
    SUM(fi.valor) AS populacao_total,
    COUNT(DISTINCT m.id_municipio) AS total_municipios,
    ROUND(AVG(fi.valor), 2) AS populacao_media_municipal
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
JOIN regioes r ON e.id_regiao = r.id_regiao
GROUP BY e.id_uf, e.nome_uf, e.sigla_uf, r.nome_regiao
ORDER BY populacao_total DESC
LIMIT 10;

-- A3: Distribuição de população por região (análise agregada)
SELECT 
    r.nome_regiao,
    COUNT(DISTINCT e.id_uf) AS total_estados,
    COUNT(DISTINCT m.id_municipio) AS total_municipios,
    SUM(fi.valor) AS populacao_total_regiao,
    ROUND(AVG(fi.valor), 2) AS populacao_media_municipal,
    MIN(fi.valor) AS populacao_minima,
    MAX(fi.valor) AS populacao_maxima,
    ROUND(CAST(SUM(fi.valor) AS REAL) /
        (SELECT SUM(valor) FROM fato_indicador_municipal) * 100, 2) AS percentual_populacao_nacional
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total_regiao DESC;

-- A4: Classificação de municípios por tamanho de população
SELECT 
    m.nome_municipio,
    e.nome_uf,
    e.sigla_uf,
    r.nome_regiao,
    fi.valor,
    CASE 
        WHEN fi.valor >= 1000000 THEN 'Metropole (>=1M)'
        WHEN fi.valor >= 100000 THEN 'Grande (100K-1M)'
        WHEN fi.valor >= 50000 THEN 'Medio (50K-100K)'
        WHEN fi.valor >= 20000 THEN 'Pequeno (20K-50K)'
        ELSE 'Muito Pequeno (<20K)'
    END AS categoria_tamanho
FROM fato_indicador_municipal fi
JOIN municipios m ON fi.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
ORDER BY fi.valor DESC;

-- A5: Municípios acima da média de população por estado
WITH media_por_estado AS (
    SELECT 
        e.id_uf,
        e.nome_uf,
        AVG(fi.valor) AS media_estado
    FROM estados e
    JOIN municipios m ON e.id_uf = m.id_uf
    LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
    GROUP BY e.id_uf, e.nome_uf
)
SELECT 
    mpe.nome_uf,
    e.sigla_uf,
    m.nome_municipio,
    fi.valor,
    ROUND(fi.valor - mpe.media_estado, 2) AS diferenca_media,
    ROUND((fi.valor / mpe.media_estado - 1) * 100, 2) AS percentual_acima_media
FROM media_por_estado mpe
JOIN estados e ON mpe.id_uf = e.id_uf
JOIN municipios m ON e.id_uf = m.id_uf
JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
WHERE fi.valor > mpe.media_estado
ORDER BY mpe.nome_uf, fi.valor DESC;

-- A6: Concentração de população - Regra de Pareto por região
WITH base AS (
    SELECT 
        r.id_regiao,
        r.nome_regiao,
        m.nome_municipio,
        e.nome_uf,
        fi.valor,
        SUM(fi.valor) OVER (PARTITION BY r.id_regiao) AS populacao_total_regiao
    FROM regioes r
    JOIN estados e ON r.id_regiao = e.id_regiao
    JOIN municipios m ON e.id_uf = m.id_uf
    JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
),
acumulado AS (
    SELECT
        id_regiao,
        nome_regiao,
        nome_municipio,
        nome_uf,
        valor,
        populacao_total_regiao,
        SUM(valor) OVER (
            PARTITION BY id_regiao
            ORDER BY valor DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS populacao_acumulada
    FROM base
)
SELECT 
    nome_regiao,
    COUNT(*) AS municipios_ate_80_pct,
    SUM(valor) AS populacao_concentrada,
    ROUND(MAX(populacao_acumulada) * 100.0 / MAX(populacao_total_regiao), 2) AS percentual_concentracao
FROM acumulado
WHERE populacao_acumulada <= (populacao_total_regiao * 0.80)
GROUP BY nome_regiao
ORDER BY percentual_concentracao DESC;
