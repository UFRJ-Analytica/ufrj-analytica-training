-- ============================================================================
-- EXPLORAÇÃO — Evento "Champions League Winner 2025" (event_id = 12585)
-- 4 mercados de time comparados: Aston Villa, Borussia Dortmund, PSG, Young Boys
-- Todas as queries rodam a partir do projeto pessoal do trainee, referenciando
-- o projeto de treinamento pelo caminho completo entre crases.
-- ============================================================================

-- Exploração 1: todos os mercados de time do evento Champions League Winner 2025
-- Pergunta: quais times têm mercado nesse evento, e qual o volume de cada um?
-- (usado para escolher os 4 mercados com trajetórias distintas comparados aqui)
SELECT market_id, question, volume, created_at, end_date, closed
FROM `even-continuity-441808-j0.polymarket_optimized.markets`
WHERE event_id = '12585'          -- event_id é STRING: usar aspas
ORDER BY volume DESC;

-- Exploração 2: série diária dos 4 mercados selecionados
-- Pergunta: como a probabilidade implícita e o volume diário evoluíram em cada
-- um dos 4 times ao longo da campanha?
SELECT market_id, trade_date, avg_trade_price, min_trade_price, max_trade_price,
       daily_trade_count, daily_usd_volume, rolling_7d_avg_volume
FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
WHERE market_id IN ('507286','507294','507305','507319')
ORDER BY market_id, trade_date;

-- Exploração 3: volatilidade diária dos 4 mercados
-- Pergunta: em quais dias/mercados os preços negociados foram mais dispersos,
-- indicando baixa liquidez ou ruído na formação de preço?
SELECT market_id, trade_date, price_volatility, avg_price_deviation,
       max_price_deviation, matched_trades, rolling_7d_avg_deviation
FROM `even-continuity-441808-j0.polymarket_mart.v_price_quality_daily`
WHERE market_id IN ('507286','507294','507305','507319')
ORDER BY market_id, trade_date;

-- Exploração 4: rótulos (nome do time por market_id)
-- Pergunta: qual pergunta/janela temporal/status corresponde a cada market_id?
-- (usado no notebook para montar o dicionário market_id -> nome do time)
SELECT market_id, question, created_at, end_date, closed
FROM `even-continuity-441808-j0.polymarket_optimized.markets`
WHERE market_id IN ('507286','507294','507305','507319')
ORDER BY market_id;
