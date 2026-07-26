-- BANCO DE DADOS II - BigQuery Queries
-- Análise de Eventos Polymarket
-- Projeto: even-continuity-441808-j0
-- Dataset: polymarket_events

-- ==============================================================================
-- Q1: Volume de Transações por Tipo de Mercado
-- Objetivo: Identificar mercados mais ativos por volume total
-- ==============================================================================
SELECT 
  market_category,
  COUNT(DISTINCT market_id) as total_mercados,
  COUNT(*) as total_transacoes,
  SUM(volume) as volume_total,
  AVG(volume) as volume_medio,
  MAX(volume) as volume_maximo,
  ROUND(SUM(volume * price) / 1000000, 2) as valor_total_milhoes,
  ROUND(100.0 * SUM(volume) / (SELECT SUM(volume) FROM polymarket_events.transactions), 2) as pct_do_total
FROM 
  `even-continuity-441808-j0.polymarket_events.transactions`
WHERE 
  DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY 
  market_category
ORDER BY 
  volume_total DESC;


-- ==============================================================================
-- Q2: Distribuição de Preços ao Longo do Tempo
-- Objetivo: Analisar evolução de preços por mercado no período
-- ==============================================================================
SELECT 
  market_id,
  market_description,
  DATE(timestamp) as data,
  MIN(price) as preco_minimo,
  MAX(price) as preco_maximo,
  AVG(price) as preco_medio,
  STDDEV(price) as desvio_preco,
  COUNT(*) as total_transacoes,
  SUM(volume) as volume_diario
FROM 
  `even-continuity-441808-j0.polymarket_events.transactions`
WHERE 
  DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY 
  market_id,
  market_description,
  DATE(timestamp)
ORDER BY 
  market_id,
  data DESC;


-- ==============================================================================
-- Q3: Ranking de Mercados por Liquidez
-- Objetivo: Identifica mercados com maior liquidez = volume * spread médio
-- ==============================================================================
WITH market_metrics AS (
  SELECT 
    market_id,
    market_description,
    market_category,
    COUNT(DISTINCT DATE(timestamp)) as dias_ativos,
    SUM(volume) as volume_total,
    AVG(price * (1 - price)) as spread_medio,  -- Spread aproximado (price * (1-price))
    MAX(timestamp) as ultima_transacao,
    ROW_NUMBER() OVER (PARTITION BY market_category ORDER BY SUM(volume) DESC) as ranking_categoria
  FROM 
    `even-continuity-441808-j0.polymarket_events.transactions`
  WHERE 
    DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY 
    market_id,
    market_description,
    market_category
)
SELECT 
  market_id,
  market_description,
  market_category,
  dias_ativos,
  volume_total,
  ROUND(spread_medio, 4) as spread_medio,
  ROUND(volume_total * spread_medio, 2) as liquidez_score,
  ranking_categoria,
  ultima_transacao
FROM 
  market_metrics
WHERE 
  ranking_categoria <= 5  -- Top 5 por categoria
ORDER BY 
  market_category,
  liquidez_score DESC;


-- ==============================================================================
-- ALERTA 1: Movimentos de Preço Anômalos (>10% em 24h)
-- Objetivo: Detectar mudanças de preço superiores a 10% em janelas de 24 horas
-- ==============================================================================
WITH price_changes AS (
  SELECT 
    market_id,
    market_description,
    DATE(timestamp) as data,
    HOUR(timestamp) as hora,
    FIRST_VALUE(price) OVER (
      PARTITION BY market_id, DATE(timestamp), HOUR(timestamp) 
      ORDER BY timestamp
    ) as preco_inicio_hora,
    LAST_VALUE(price) OVER (
      PARTITION BY market_id, DATE(timestamp) 
      ORDER BY timestamp 
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as preco_fim_dia,
    FIRST_VALUE(price) OVER (
      PARTITION BY market_id, DATE(timestamp) 
      ORDER BY timestamp
    ) as preco_inicio_dia,
    timestamp
  FROM 
    `even-continuity-441808-j0.polymarket_events.transactions`
  WHERE 
    DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
)
SELECT 
  market_id,
  market_description,
  data,
  preco_inicio_dia,
  preco_fim_dia,
  ROUND(ABS(preco_fim_dia - preco_inicio_dia), 4) as variacao_absoluta,
  ROUND(100.0 * (preco_fim_dia - preco_inicio_dia) / NULLIF(preco_inicio_dia, 0), 2) as variacao_pct,
  CASE 
    WHEN ABS(100.0 * (preco_fim_dia - preco_inicio_dia) / NULLIF(preco_inicio_dia, 0)) > 10 THEN '🔴 ALERTA'
    WHEN ABS(100.0 * (preco_fim_dia - preco_inicio_dia) / NULLIF(preco_inicio_dia, 0)) > 5 THEN '🟡 ATENÇÃO'
    ELSE '🟢 NORMAL'
  END as status_alerta
FROM 
  price_changes
WHERE 
  ABS(100.0 * (preco_fim_dia - preco_inicio_dia) / NULLIF(preco_inicio_dia, 0)) > 5
GROUP BY 
  market_id,
  market_description,
  data,
  preco_inicio_dia,
  preco_fim_dia
ORDER BY 
  data DESC,
  variacao_pct DESC;


-- ==============================================================================
-- ALERTA 2: Volume Atípico (>2 desvios padrão)
-- Objetivo: Identifica períodos com volume fora do padrão normal
-- ==============================================================================
WITH volume_stats AS (
  SELECT 
    market_id,
    market_description,
    AVG(volume) as volume_medio,
    STDDEV(volume) as desvio_volume,
    MAX(volume) as volume_maximo,
    MIN(volume) as volume_minimo
  FROM 
    `even-continuity-441808-j0.polymarket_events.transactions`
  WHERE 
    DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY 
    market_id,
    market_description
),
volume_desvios AS (
  SELECT 
    t.market_id,
    t.market_description,
    DATE(t.timestamp) as data,
    HOUR(t.timestamp) as hora,
    t.volume,
    vs.volume_medio,
    vs.desvio_volume,
    ROUND((t.volume - vs.volume_medio) / NULLIF(vs.desvio_volume, 0), 2) as z_score,
    COUNT(*) as total_transacoes
  FROM 
    `even-continuity-441808-j0.polymarket_events.transactions` t
  JOIN 
    volume_stats vs ON t.market_id = vs.market_id
  WHERE 
    DATE(t.timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  GROUP BY 
    t.market_id,
    t.market_description,
    DATE(t.timestamp),
    HOUR(t.timestamp),
    t.volume,
    vs.volume_medio,
    vs.desvio_volume
)
SELECT 
  market_id,
  market_description,
  data,
  hora,
  volume,
  ROUND(volume_medio, 2) as volume_medio_historico,
  ROUND(desvio_volume, 2) as desvio_padrao,
  z_score,
  total_transacoes,
  CASE 
    WHEN ABS(z_score) > 3 THEN '🔴 CRÍTICO'
    WHEN ABS(z_score) > 2 THEN '🔴 ALERTA'
    WHEN ABS(z_score) > 1 THEN '🟡 ATENÇÃO'
    ELSE '🟢 NORMAL'
  END as status_volume
FROM 
  volume_desvios
WHERE 
  ABS(z_score) > 2
ORDER BY 
  data DESC,
  ABS(z_score) DESC;


-- ==============================================================================
-- Q6: Análise de Participantes por Mercado
-- Objetivo: Entender distribuição de traders e concentração de volume
-- ==============================================================================
SELECT 
  market_id,
  market_description,
  COUNT(DISTINCT participant_id) as total_participantes,
  COUNT(*) as total_transacoes,
  SUM(volume) as volume_total,
  ROUND(AVG(volume), 2) as volume_medio_por_tx,
  ROUND(MAX(volume), 2) as maior_transacao,
  ROUND(STDDEV(volume), 2) as desvio_volume,
  ROUND(
    100.0 * SUM(CASE WHEN volume > (SELECT PERCENTILE_CONT(volume, 0.95) 
                                     FROM `even-continuity-441808-j0.polymarket_events.transactions` 
                                     WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY))
    THEN volume ELSE 0 END) / SUM(volume), 
    2
  ) as pct_volume_top5pct
FROM 
  `even-continuity-441808-j0.polymarket_events.transactions`
WHERE 
  DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY 
  market_id,
  market_description
ORDER BY 
  volume_total DESC;
