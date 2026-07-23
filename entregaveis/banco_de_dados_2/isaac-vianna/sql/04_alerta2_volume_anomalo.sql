-- ALERTA 2 — Volume anômalo (Rolling Window de 7 dias)
-- Mercado: "Will Aston Villa win the UEFA Champions League?" (market_id 507286)
--
-- Pergunta: em quais dias a atividade de negociação surtou muito acima do normal?
--
-- Regra: volume do dia >= 2.5x a média móvel de 7 dias  E  >= 10.000 USD.
-- O piso absoluto evita disparos em dias iniciais com média móvel minúscula.
--
-- Metodologia: Rolling Window (rolling_7d_avg_volume já vem calculada na view).
-- Sinaliza surtos tipicamente associados a jogos e à definição do chaveamento.
--
-- Otimização: view agregada v_market_daily; sem SELECT *; sem funções voláteis
-- de data (mercado fechado, dataset estático — favorece cache de resultados).

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
  WHERE market_id = '507286'
)
SELECT
  market_id,
  trade_date,
  probabilidade_atual,
  volume_atual,
  volume_medio_7d,
  ROUND(razao_vol, 2) AS razao_vol_sobre_media,
  trades_dia,
  'volume_anomalo' AS tipo_alerta
FROM serie
WHERE razao_vol    >= 2.5         -- volume >= 2,5x a média móvel de 7 dias
  AND volume_atual >= 10000       -- piso absoluto de liquidez
ORDER BY razao_vol DESC;
