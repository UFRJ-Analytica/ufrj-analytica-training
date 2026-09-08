
# banco de dados 2 - polymarket no bigquery

## trainee

miguel marques

## mercado escolhido

will paris saint-germain win the uefa champions league?
(market_id: 507305)

## pergunta central

como o volume de apostas se comportou conforme o psg avancou na champions league?

## hipotese inicial

a expectativa e que o volume negociado aumente conforme o psg avanca na competicao, principalmente nas fases finais

## periodo analisado

2024-09-17 (criacao do mercado) ate 2025-05-31 (fechamento, dia da final)

## tabelas/datasets usados no bigquery

- `polymarket_optimized.markets` - informacoes gerais do mercado escolhido
- `polymarket_mart.daily_market_stats` - serie diaria agregada (volume, preco medio, min/max) usada em toda a analise

## arquivos sql e alertas

- **exploracao inicial**: query em `markets` pra confirmar o mercado certo, e query em `daily_market_stats` pra trazer a serie diaria completa
- **metricas**: query com CTE calculando volume/preco do dia anterior (LAG) e media movel de 7 dias do volume, base pros dois alertas
- **alerta de volume**: dispara quando o volume do dia fica 2x ou mais acima da media movel de 7 dias
- **alerta de preco**: dispara quando o preco medio varia 0.10 ou mais em relacao ao dia anterior

## resultado final

o alerta de volume teve assertividade de 15.4% (acima do esperado por acaso, ~8.2%), indicando que ele capta reacao real do mercado a jogos decisivos. o alerta de preco teve assertividade de 5.3% (abaixo do acaso), sugerindo que ele capta mais ruido geral do mercado do que reacao especifica a jogo. a hipotese se confirma em parte: o mercado reage mais perto de jogo importante, mas nem todo alerta capta isso do mesmo jeito

## dados

os csvs usados na analise estao na pasta `dados/` e tambem disponiveis no google drive:
[[drive.google.com/drive/folders/1mRj45wqiLOGmSxY_d_oU6V6XVprwHygK?usp=sharing](https://drive.google.com/drive/folders/1mRj45wqiLOGmSxY_d_oU6V6XVprwHygK?usp=sharing)]
