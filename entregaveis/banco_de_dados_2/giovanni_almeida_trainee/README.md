## Nome
# Giovanni Faletti Almeida

## Evento
# Trump ends Ukraine war in first 90 days?
## Pergunta de Pesquisa
Como se comportou o mercado com os momentos iniciais do governo de trump?
## Hipótese inicial
 Minha hipótese central é que o característico alto ruído de comunicação do governo Trunp o fez perder confiança e "jogar" a vantagem para o "no".
## Tabelas/datasets usados no BigQuery
polymarket_optimized.trades, polymarket_optimized.markets,polymarket_mart.v_market_daily
## Período analisado
O período inicial do governo de Trump:
2025-01-01 até 2025-02-28.
## Descrição SQL e alertas
Usei queries de agregação para volume de trades, probabilidade implícita, spread diário de preço e desvio padrão de preço. Os alertas se basearam em Z-Scores e uma lógica de mudança de fluxo para um dado caso específico ('No'), e foram validados usando o próprio mercado, mas por um período extendido (além dos períodos iniciais do governo de Trump).

# Link google drive dados
https://drive.google.com/drive/folders/1UR5-YY_RPeMw5g3zA-I6nH4zwyceoNq5?usp=sharing