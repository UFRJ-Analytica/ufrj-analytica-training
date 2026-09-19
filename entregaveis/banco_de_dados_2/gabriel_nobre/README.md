**nome do trainee:** Gabriel Nobre

**Evento escolhido:** FURIA vs Vitality (BO5) - IEM Krakow 2026 (Counter Strike)

**Pergunta Central:** Houve alteração brusca na probabilidade implícita ou algum pico de volume anômalo durante a série entre FURIA e Vitality?

**Hipótese Inicial**: O volume de apostas tende a ser maior durante o desenrolar do jogo, especialmente em rounds críticos e outros momentos decisivos.

**Período Analisado:** 07 de fevereiro de 2026 a 08 de fevereiro de 2026.(período no qual o jogo foi confirmado até o fim da partida)

**Datasets Utilizados:** 

Polymarket_mart
    daily_market_stats

Polymarket_optimized
    trades
    markets

**Descrição dos arquivos SQL e alertas:**
    1. Consulta de baseline diário, analisando o volume total em dólares, preço mínimos, máximos e médios da tabela.

    2. Consulta dos trades, analisando o momento, valor do trade, para qual lado está acontecendo a aposta e etc.

    3. Consulta unificada com alertas, criando alertas para um volume maior que o normal, analisando as últimas horas e as utilizando como base. Além disso, cria um alerta também quando há oscilações na média entre as horas.

**Link público da pasta:**  https://drive.google.com/drive/folders/1XeFcPenjxytf_sXwyp_X1sbHvSdOpAI9?usp=sharing


