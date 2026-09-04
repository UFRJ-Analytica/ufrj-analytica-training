-- ============================================================================
-- AGREGAÇÃO ANALÍTICA — variação diária de probabilidade e razão de volume,
-- por mercado (multi-mercado: Aston Villa, Borussia Dortmund, PSG, Young Boys)
--
-- Otimização adotada (ver seção 7 do enunciado):
--  - Usamos a view agregada `v_market_daily` (processa MB, não GB), em vez da
--    tabela transacional `polymarket_optimized.trades`.
--  - A função de janela (LAG) é declarada dentro de uma CTE ("serie") com
--    PARTITION BY market_id — isso faz a janela rodar corretamente para vários
--    mercados de uma só vez, sem vazar valores entre times. A filtragem final
--    ocorre com WHERE simples no bloco externo.
--  - Sem SELECT *; datas literais não são necessárias aqui pois filtramos por
--    market_id IN (...) (mercados fechados, dataset estático) — favorece cache.
-- ============================================================================
WITH serie AS (
  SELECT
    market_id,
    trade_date,
    avg_trade_price                                   AS probabilidade,
    LAG(avg_trade_price) OVER (
      PARTITION BY market_id ORDER BY trade_date)     AS probabilidade_anterior,
    daily_usd_volume                                  AS volume_dia,
    rolling_7d_avg_volume                             AS volume_medio_7d
  FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
  WHERE market_id IN ('507286','507294','507305','507319')
)
SELECT
  market_id, trade_date, probabilidade,
  ROUND(probabilidade - probabilidade_anterior, 4)    AS variacao_probabilidade,
  volume_dia, volume_medio_7d,
  ROUND(SAFE_DIVIDE(volume_dia, volume_medio_7d), 2)  AS razao_volume
FROM serie
WHERE probabilidade_anterior IS NOT NULL
ORDER BY market_id, trade_date;
