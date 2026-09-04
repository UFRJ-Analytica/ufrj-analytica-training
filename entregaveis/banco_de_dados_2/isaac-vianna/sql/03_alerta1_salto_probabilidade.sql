-- ============================================================================
-- ALERTA 1 — Salto de probabilidade confirmado por liquidez (multi-mercado)
-- Mercados: Aston Villa (507286), Borussia Dortmund (507294), PSG (507305),
--           Young Boys (507319) — todos do evento Champions League Winner 2025
--
-- Pergunta: em quais dias, em cada um desses mercados, a probabilidade
-- implícita mudou bruscamente de forma confiável (não por ruído de dia seco)?
--
-- Regra: |variação da probabilidade dia-a-dia| >= 0.10  E  volume do dia >= 10.000 USD.
-- A trava de volume evita disparos falsos causados por médias de preço instáveis
-- em dias de baixíssima liquidez.
--
-- Generalização: PARTITION BY market_id faz o LAG (e portanto a variação)
-- rodar por mercado, sem misturar valores entre times; o filtro IN (...) aplica
-- o MESMO alerta a vários mercados comparáveis de uma só vez.
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
  WHERE market_id IN ('507286','507294','507305','507319')
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
  market_id, trade_date, probabilidade_anterior, probabilidade_atual,
  variacao_probabilidade, volume_atual, volume_medio_7d, trades_dia,
  'salto_probabilidade' AS tipo_alerta
FROM com_variacao
WHERE variacao_abs >= 0.10        -- salto relevante de probabilidade
  AND volume_atual  >= 10000      -- confirmação de liquidez
ORDER BY market_id, variacao_abs DESC;
