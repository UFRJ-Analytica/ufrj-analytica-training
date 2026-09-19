# Banco de Dados II — Polymarket no BigQuery

**Trainee:** Gabriel Basto
**Evento/mercado escolhido:** Mercado `market_id = 547977` — *"Will Chelsea win the FIFA Club World Cup?"* (evento "FIFA Club World Cup Winner"), volume total ~US$ 2,31 milhões, criado em 28/05/2025. O Chelsea venceu o Fluminense por 2-0 na semifinal (08/07/2025) e o PSG por 3-0 na final (13/07/2025), disputada no MetLife Stadium (Nova Jersey/EUA), sagrando-se campeão. Mercado `closed = 1` (totalmente resolvido, dentro da janela de dados disponível).

## Pergunta central

Como a probabilidade implícita (preço do contrato "Chelsea vence o Mundial de Clubes 2025") e o volume negociado nesse mercado do Polymarket se comportaram nos dias que antecederam, durante e imediatamente após a semifinal (08/07) e a final (13/07/2025)?

## Hipótese inicial

O volume negociado e a volatilidade da probabilidade implícita aumentam de forma acentuada nas horas anteriores e durante cada jogo eliminatório do Chelsea, com um salto abrupto na probabilidade logo após cada resultado (vitória sobre o Fluminense na semifinal, vitória sobre o PSG na final), à medida que o contrato se aproxima da resolução ($1 para o campeão).

> Observação: a análise evita afirmar causalidade estrita — trata-se de observar correlação temporal entre os resultados dos jogos e a reação de preço/volume, discutindo limitações (ex: dados de jogo, como gols e cartões, não estão no dataset, apenas inferidos pelos saltos de preço/volume).

## Tabelas/datasets utilizados no BigQuery

- `even-continuity-441808-j0.polymarket_optimized.markets` — metadados do mercado do Chelsea no Mundial de Clubes 2025 (market_id, question, event_title, volume, created_at, end_date, closed, token1/token2, answer1/answer2).
- `even-continuity-441808-j0.polymarket_optimized.trades` — transações individuais, particionadas por dia (`trade_timestamp`) e clusterizadas por `market_id`, usadas para os alertas de granularidade fina ao redor da semifinal e da final.
- `even-continuity-441808-j0.polymarket_mart.v_market_daily` e `v_price_quality_daily` — agregados diários já prontos (incluindo médias móveis de 7 dias), usados na exploração inicial e tendência ao longo do torneio (menor custo de scan).

## Período analisado

Do início do torneio (14/06/2025) até alguns dias após a final (15/07/2025), com foco de granularidade fina na janela **07/07/2025 a 14/07/2025** (semifinal → final → resolução).

## Arquivos

- `relatorio.ipynb`: notebook central com exploração inicial, agregações, os dois alertas finais e a visualização com métricas de assertividade.
- `dados/`: CSVs exportados do BigQuery (não versionados no Git — bloqueados via `.gitignore`). Os arquivos usados na análise estão disponíveis publicamente em: **[https://drive.google.com/drive/folders/1xq9lltL0EwpNeH50olIPETN2Nl2yaCfC]**

## Resumo dos dois alertas

1. **Alerta de Volume Anômalo (Z-score de volume):** sinaliza janelas em que o volume negociado do mercado do Chelsea está estatisticamente muito acima da média móvel recente (ex: |z| > 2), indicando possível reação a um evento externo (jogo decisivo, gol, resultado).
2. **Alerta de Variação Brusca de Probabilidade (Rolling Window):** sinaliza janelas em que a variação da probabilidade implícita entre um período e o anterior ultrapassa um limiar definido, capturando choques de informação (ex: salto após a vitória na semifinal ou na final).

## Como reproduzir

1. Baixar os CSVs do link do Google Drive acima e colocar na pasta `dados/` (mesma estrutura de nomes usada no notebook).
2. Abrir `relatorio.ipynb` e rodar as células em ordem — as células de SQL devem ser executadas manualmente no BigQuery Studio (projeto pessoal, referenciando `even-continuity-441808-j0` no FROM), e o resultado exportado como CSV para `dados/`.
