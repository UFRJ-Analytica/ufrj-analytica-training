# Banco de Dados II - UFRJ Analytica

## Trainee
Julio Cesar

## Mercado escolhido
Will Bitcoin reach $1,000,000 by December 31, 2025?

## Pergunta da análise
Como o volume financeiro e a probabilidade implícita se comportaram ao longo do período e quais padrões podem ser utilizados para gerar alertas automáticos?

## Hipótese
Períodos de maior atividade do mercado apresentam volumes financeiros significativamente superiores ao comportamento histórico e mudanças bruscas na probabilidade implícita.

## Datasets utilizados
- polymarket_mart.daily_market_stats

## Período analisado
2024-12-30 a 2026-01-01

## Arquivos da entrega

- **relatorio.ipynb:** análise completa, EDA, visualizações e validação dos alertas.
- **dados/**: arquivos CSV utilizados na análise.
- **alerta_volume.sql:** identifica dias com volume financeiro acima da média acrescida de dois desvios-padrão.
- **alerta_probabilidade.sql:** identifica dias com variações anormais da probabilidade implícita.

## Alertas implementados

- **Alerta 1:** Volume financeiro diário acima da média + 2 desvios-padrão.
- **Alerta 2:** Variação diária da probabilidade implícita acima da média + 2 desvios-padrão.

## Google Drive

Link para a pasta contendo os arquivos CSV utilizados na análise:

https://drive.google.com/drive/folders/1BUCLC_2pMdyezilTLs-GI0RtelT8MZdX?usp=drive_link