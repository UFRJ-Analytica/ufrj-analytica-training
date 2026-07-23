# Banco de Dados II — Entrega Individual

**Trainee:** Isaac Vianna

## Evento/mercado escolhido

**"Will Aston Villa win the UEFA Champions League?"** (`market_id = 507286`), parte do evento `Champions League Winner` (`event_id = 12585`, slug `champions-league-winner-2025`) do Polymarket. Mercado fechado (`closed = 1`), criado em 2024-09-17, com `end_date` em 2025-05-31.

## Pergunta central

Como o volume negociado e a probabilidade implícita do mercado reagiram aos jogos do Aston Villa e à evolução do chaveamento ao longo da campanha 2024-25 da Champions League?

## Hipótese inicial

Os maiores saltos de probabilidade e os picos de volume se concentram em torno das datas de jogos do Villa e dos eventos de definição do mata-mata. Movimentos em dias de baixa liquidez são majoritariamente ruído, não reprecificação real.

## Tabelas/datasets utilizados (BigQuery)

- `polymarket_optimized.markets` — metadados do mercado.
- `polymarket_mart.daily_market_stats` — cobertura temporal (primeiro/último dia com dados, volume total).
- `polymarket_mart.v_market_daily` — série diária de probabilidade implícita, preços e volume, com média móvel de 7 dias.
- `polymarket_mart.v_price_quality_daily` — volatilidade e desvio de preço diário.

Todas as queries referenciam o projeto de treinamento (`even-continuity-441808-j0`) pelo caminho completo entre crases, rodando a partir do projeto pessoal do trainee (ver `sql/`).

## Período analisado

**2024-09-17 a 2025-04-15 (211 dias)**. Os dados terminam no dia da eliminação do Villa (jogo de volta das quartas de final vs PSG, 15/04/2025).

## Estrutura da pasta

```
entregaveis/banco_de_dados_2/isaac-vianna/
  README.md
  relatorio.ipynb        # análise completa (lê apenas os CSVs de dados/)
  sql/
    01_exploracao.sql              # as 4 queries de coleta/exploração
    02_agregacoes.sql              # variação de probabilidade + razão de volume (LAG em CTE)
    03_alerta1_salto_probabilidade.sql
    04_alerta2_volume_anomalo.sql
  dados/                  # CSVs locais (ignorados pelo git — baixar do Drive, ver abaixo)
```

## Arquivos SQL e os dois alertas

- **`01_exploracao.sql`** — as 4 queries de exploração inicial: metadados do mercado, cobertura temporal, série diária e volatilidade diária. Foram as queries que geraram os CSVs de `dados/`.
- **`02_agregacoes.sql`** — consulta analítica que deriva a variação diária de probabilidade (`LAG` em CTE) e a razão volume/média-móvel, base para os dois alertas. Usa a view agregada `v_market_daily` (MB, não GB) em vez da tabela transacional `trades`.
- **`03_alerta1_salto_probabilidade.sql`** — **Alerta 1**: sinaliza dias em que a probabilidade implícita mudou bruscamente (`|variação| >= 0.10`) **e** o volume do dia confirma liquidez (`>= US$ 10.000`), evitando falsos positivos causados por médias de preço instáveis em dias secos. Retorna 12 registros no período.
- **`04_alerta2_volume_anomalo.sql`** — **Alerta 2**: sinaliza dias em que o volume surtou muito acima do normal (`>= 2,5x a média móvel de 7 dias`), com piso absoluto de `US$ 10.000` para evitar disparos em dias iniciais com média móvel minúscula (metodologia Rolling Window). Retorna 19 registros no período.

Os dois alertas juntos somam mais de 70 linhas comentadas e retornam apenas os registros considerados relevantes pelas regras. O `relatorio.ipynb` reproduz as mesmas regras em pandas (com os thresholds expostos como variáveis), exibe o SQL como artefato e calcula a assertividade de cada alerta contra as datas reais de jogos do Villa.

## Como reproduzir

Os CSVs usados nesta análise estão disponíveis publicamente no Google Drive:

**Link do Drive:** https://drive.google.com/drive/folders/19AntdxijbWzIBn4rCDPNA4veYX_1riPm?usp=drive_link

Baixe os 4 arquivos (`mercado.csv`, `cobertura.csv`, `serie_diaria.csv`, `volatilidade_diaria.csv`) e coloque-os na pasta `dados/` desta entrega (ela é ignorada pelo git). O `relatorio.ipynb` lê apenas esses CSVs locais — nenhuma célula consulta o BigQuery ao vivo — e roda de ponta a ponta a partir daí.
