-- ============================================================================
-- ALERTA 1 — Salto de probabilidade confirmado por liquidez
-- Mercado: "Will Aston Villa win the UEFA Champions League?" (market_id 507286)
--
-- Pergunta: em quais dias a probabilidade implícita mudou bruscamente de forma
-- confiável (não por ruído de dia seco)?
--
-- Regra: |variação da probabilidade dia-a-dia| >= 0.10  E  volume do dia >= 10.000 USD.
-- A trava de volume evita disparos falsos causados por médias de preço instáveis
-- em dias de baixíssima liquidez (ex.: probabilidade "0,79" movida por ~US$186).
--
-- Otimização: view agregada v_market_daily (MB, não GB); LAG declarado em CTE
-- e filtrado com WHERE simples no bloco externo; sem SELECT *.
-- ============================================================================
WITH serie AS (
  SELECT
    market_id,
    trade_date,
    avg_trade_price                                   AS probabilidade_atual,
    LAG(avg_trade_price) OVER (
      PARTITION BY market_id ORDER BY trade_date)     AS probabilidade_anterior,
    daily_usd_volume                                  AS volume_atual,
    rolling_7d_avg_volume                             AS volume_medio_7d,
    daily_trade_count                                 AS trades_dia
  FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
  WHERE market_id = '507286'
),
com_variacao AS (
  SELECT
    *,
    ROUND(probabilidade_atual - probabilidade_anterior, 4) AS variacao_probabilidade,
    ABS(probabilidade_atual - probabilidade_anterior)      AS variacao_abs
  FROM serie
  WHERE probabilidade_anterior IS NOT NULL
)
SELECT
  market_id,
  trade_date,
  probabilidade_anterior,
  probabilidade_atual,
  variacao_probabilidade,
  volume_atual,
  volume_medio_7d,
  trades_dia,
  'salto_probabilidade' AS tipo_alerta
FROM com_variacao
WHERE variacao_abs >= 0.10        -- salto relevante de probabilidade
  AND volume_atual  >= 10000      -- confirmação de liquidez
ORDER BY variacao_abs DESC;
