-- ============================================================================
-- EXPLORAÇÃO — Mercado "Will Aston Villa win the UEFA Champions League?"
-- market_id = 507286 | event_id = 12585 | slug = champions-league-winner-2025
-- Todas as queries rodam a partir do projeto pessoal do trainee, referenciando
-- o projeto de treinamento pelo caminho completo entre crases.
-- ============================================================================

-- Exploração 1: metadados do mercado escolhido
-- Pergunta: quem é esse mercado (pergunta, evento, janela temporal, status)?
SELECT market_id, question, event_title, event_id, event_slug,
       volume, created_at, end_date, closed, outcome_prices, token1, token2
FROM `even-continuity-441808-j0.polymarket_optimized.markets`
WHERE market_id = '507286';

-- Exploração 2: cobertura temporal do mercado (define a janela da análise)
-- Pergunta: qual o primeiro e o último dia com dados, e quanto volume foi
-- negociado no total nesse intervalo?
SELECT MIN(trade_date) AS primeiro_dia, MAX(trade_date) AS ultimo_dia,
       COUNT(*) AS dias_com_dados, SUM(daily_usd_volume) AS volume_total
FROM `even-continuity-441808-j0.polymarket_mart.daily_market_stats`
WHERE market_id = '507286';

-- Exploração 3: série diária — probabilidade implícita, volume e média móvel de 7 dias
-- Pergunta: como a probabilidade implícita (avg_trade_price) e o volume diário
-- evoluíram ao longo da campanha?
SELECT trade_date, avg_trade_price, min_trade_price, max_trade_price,
       daily_trade_count, daily_usd_volume, rolling_7d_avg_volume
FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
WHERE market_id = '507286'
ORDER BY trade_date;

-- Exploração 4: volatilidade / qualidade de preço diária
-- Pergunta: em quais dias os preços negociados foram mais dispersos/instáveis,
-- indicando baixa liquidez ou ruído na formação de preço?
SELECT trade_date, price_volatility, avg_price_deviation, max_price_deviation,
       matched_trades, rolling_7d_avg_deviation
FROM `even-continuity-441808-j0.polymarket_mart.v_price_quality_daily`
WHERE market_id = '507286'
ORDER BY trade_date;
