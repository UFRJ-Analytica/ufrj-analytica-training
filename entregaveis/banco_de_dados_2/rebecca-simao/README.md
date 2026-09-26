# Banco de Dados II - Polymarket no BigQuery - Rebecca Gomes Simão

Mercado escolhido: DeepSeek banned in US before April?
market_id: 519801

## Pergunta central

Quais dias apresentaram atividade anormal nesse mercado e em que medida diferentes regras de alerta conseguem identificar esses períodos?

## Hipótese

Dias com volume ou quantidade de negociações muito acima do comportamento recente podem estar relacionados a acontecimentos relevantes para o mercado.

## Período analisado

23 de janeiro a 1º de abril de 2025.

## Tabelas utilizadas no BigQuery

even-continuity-441808-j0.polymarket_mart.v_top_markets
even-continuity-441808-j0.polymarket_mart.v_market_daily
even-continuity-441808-j0.polymarket_optimized.trades

## Alertas

### Alerta 1: Aumento de volume e negociações

Identifica dias em que o volume foi pelo menos duas vezes maior que a média dos sete dias anteriores e a quantidade de negociações ficou entre os 25% maiores valores do período.

### Alerta 2: mudança brusca na expectativa

Identifica dias em que a probabilidade implícita do resultado YES variou pelo menos 3 pontos percentuais, com no mínimo 30 negociações.

## Arquivos

- relatorio.ipynb: análise completa, consultas SQL, resultados e visualizações;
- dados/: arquivos CSV exportados do BigQuery.
- Dados utilizados: https://drive.google.com/drive/folders/1jAgKuUvyURHuY61RURHu961vA2Lf1mT3?usp=sharing