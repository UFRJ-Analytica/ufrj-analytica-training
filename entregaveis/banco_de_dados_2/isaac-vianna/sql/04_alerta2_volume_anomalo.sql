-- ============================================================================
-- ALERTA 2 — Volume anômalo via Rolling Window de 7 dias (multi-mercado)
-- Mercados: Aston Villa (507286), Borussia Dortmund (507294), PSG (507305),
--           Young Boys (507319) — todos do evento Champions League Winner 2025
--
-- Pergunta: em quais dias, em cada um desses mercados, a atividade de
-- negociação surtou muito acima do normal?
--
-- Regra: volume do dia >= 2.5x a média móvel de 7 dias  E  >= 10.000 USD.
-- O piso absoluto evita disparos em dias iniciais com média móvel minúscula.
--
-- Metodologia: Rolling Window (rolling_7d_avg_volume já vem calculada na view).
-- Generalização: o mesmo alerta roda para os 4 mercados via IN (...); a média
-- móvel já vem particionada por mercado na view de origem.
--
-- Otimização: view agregada v_market_daily; sem SELECT *; sem funções voláteis
-- de data (mercados fechados/estáticos — favorece cache de resultados).
-- ============================================================================
WITH serie AS (
  SELECT
    market_id,
    trade_date,
    avg_trade_price                                   AS probabilidade_atual,
    daily_usd_volume                                  AS volume_atual,
    rolling_7d_avg_volume                             AS volume_medio_7d,
    daily_trade_count                                 AS trades_dia,
    SAFE_DIVIDE(daily_usd_volume, rolling_7d_avg_volume) AS razao_vol
  FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
  WHERE market_id IN ('507286','507294','507305','507319')
)
SELECT
  market_id, trade_date, probabilidade_atual, volume_atual, volume_medio_7d,
  ROUND(razao_vol, 2) AS razao_vol_sobre_media, trades_dia,
  'volume_anomalo' AS tipo_alerta
FROM serie
WHERE razao_vol    >= 2.5         -- volume >= 2,5x a média móvel de 7 dias
  AND volume_atual >= 10000       -- piso absoluto de liquidez
ORDER BY market_id, razao_vol DESC;
