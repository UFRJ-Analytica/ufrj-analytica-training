## Banco de Dados II — Entrega Polymarket no BigQuery

**Trainee:** Arthur Monteiro C. Pereira

### Evento 

Mercado `253591` - *"Will Donald Trump win the 2024 US Presidential Election?"*, o mercado de maior volume
(~US$1,53 bi, segundo o campo `volume` de `markets`) do evento Presidential Election Winner 2024 no Polymarket.

A escolha também foi parcialmente motivada por reportagens da imprensa (CNBC, WSJ, CBS News) sobre um trader francês identificado como
"Théo", que operou em diversas contas, somando mais de US$ 85 milhões apostados na vitória de Trump.


### Pergunta central
Dá para pegar os dados de negociação do mercado 253591 e achar um padrão fora do comum de acumulação? No qual haja pouca gente comprando um volume muito acima da média, bem antes dos momentos de virada da campanha, que bata com a história do "Trump Whale" que saiu na imprensa?

### Hipótese inicial
A ideia inicial é encontrar um conjunto de carteiras apostando pesado no "Trump vence", com um volume bem maior que o de um trader comum, e que se iniciaram por voltar de outubro de 2024. Obviamente, olhando só para os dados on-chain (sem os nomes de usuário da Polymarket em si), não é possível dizer com absoluta certeza que se trata das mesmas contas das notícias, mas já serve para mostrar se o padrão é coerente.

### datasets utilizados

- `polymarket_mart.v_market_daily`
- `polymarket_mart.daily_market_stats`
- `polymarket_mart.daily_user_stats`
- `polymarket_optimized.trades`
- `polymarket_optimized.markets`

### Período analisado

Período em que o mercado ficou ativo: 05/01/2024 a 06/11/2024. 
Janela de interesse para os alertas e a investigação detalhada: outubro–novembro de 2024 (reta final da campanha até a apuração).

### Arquivos SQL e alerta final

- **Query A** - série diária do mercado (volume, trades, preço médio), tabela mart.
- **Query B** - top 20 endereços por volume total no mercado.
- **Query C** - atividade hora a hora de um endereço específico (chegada tardia, alto volume) em torno da eleição.
- **Query D** - amostra de trades individuais desse mesmo endereço, com lado da aposta.
- **Alerta 1** (nível mercado): dias com volume diário anormal (z-score > 2 sobre `daily_market_stats`). Resultado:
  16 dias, todos entre out/2024 e nov/2024, com pico nos dois dias da eleição (05–06/11).
- **Alerta 2** (nível endereço): endereços com volume total anormal no mercado (z-score > 100 sobre
  `daily_user_stats` - corte elevado porque a distribuição de volume por trader é fortemente concentrada).
  Resultado: 4 endereços.

### Dados (CSVs)

Link do Google Drive: https://drive.google.com/drive/folders/16hdW3XImJrB_m2AOXKQE1OzVteLEZnC8

