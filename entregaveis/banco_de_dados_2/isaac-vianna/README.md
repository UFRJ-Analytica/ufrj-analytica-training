# Banco de Dados II — Entrega Individual

**Trainee:** Isaac Vianna

## Evento e mercados escolhidos

Evento **`Champions League Winner 2025`** (`event_id = 12585`) do Polymarket. Em vez de analisar um único mercado, a entrega compara **4 mercados de time** do mesmo evento, com trajetórias reais bem distintas na campanha 2024-25 — para testar se os alertas propostos são um **detector de padrão reprodutível**, e não algo preso a um único time:

| market_id | Time | Trajetória real 2024-25 | Papel no teste |
|---|---|---|---|
| `507286` | Aston Villa | eliminado nas quartas | caso base (estudo original, v1 desta entrega) |
| `507294` | Borussia Dortmund | eliminado nas quartas | similar ao Villa → o padrão se repete? |
| `507305` | Paris Saint-Germain | **campeão** (até a final, 31/05) | mercado que resolve SIM, probabilidade sobe e sustenta |
| `507319` | Young Boys | caiu na fase de liga (dez/2024) | mercado "morto" → o alerta fica quieto (falsos positivos?) |

## Pergunta central

Os padrões de salto de probabilidade e de volume anômalo detectados pelos alertas se repetem em mercados de trajetórias diferentes do mesmo evento?

## Hipótese inicial

Os alertas devem disparar em torno de movimentos estruturais reais nos mercados com campanha longa (Villa, Dortmund, PSG) e ficar quietos num mercado que morre cedo (Young Boys).

## Tabelas/datasets utilizados (BigQuery)

- `polymarket_optimized.markets` — metadados dos mercados (pergunta, período, status), usado também para montar o dicionário `market_id → nome do time`.
- `polymarket_mart.v_market_daily` — série diária de probabilidade implícita, preços e volume, com média móvel de 7 dias, para os 4 mercados.
- `polymarket_mart.v_price_quality_daily` — volatilidade e desvio de preço diário para os 4 mercados.

Todas as queries referenciam o projeto de treinamento (`even-continuity-441808-j0`) pelo caminho completo entre crases, rodando a partir do projeto pessoal do trainee (ver `sql/`).

## Período analisado

Varia por mercado, de **2024-09-17** (início comum de todos) até: Aston Villa e Borussia Dortmund **2025-04-15** (eliminação nas quartas, 211 e 210 dias); Paris Saint-Germain **2025-05-31** (final, 257 dias, campeão); Young Boys **2024-12-11** (eliminação na fase de liga, 86 dias).

## Estrutura da pasta

```
entregaveis/banco_de_dados_2/isaac-vianna/
  README.md
  relatorio.ipynb        # análise completa (lê apenas os CSVs *_multi.csv de dados/)
  sql/
    01_exploracao.sql              # mercados do evento + série + volatilidade + rótulos, multi-mercado
    02_agregacoes.sql              # variação de probabilidade + razão de volume (LAG em CTE, PARTITION BY market_id)
    03_alerta1_salto_probabilidade.sql
    04_alerta2_volume_anomalo.sql
  dados/                  # CSVs locais (ignorados pelo git — baixar do Drive, ver abaixo)
```

## Arquivos SQL e os dois alertas

- **`01_exploracao.sql`** — lista os mercados de time do evento, e coleta série diária, volatilidade e rótulos para os 4 mercados selecionados (`market_id IN (...)`).
- **`02_agregacoes.sql`** — deriva a variação diária de probabilidade (`LAG` em CTE, particionado por `market_id`) e a razão volume/média-móvel, agora para os 4 mercados de uma vez, sem misturar valores entre times.
- **`03_alerta1_salto_probabilidade.sql`** — **Alerta 1**: sinaliza dias em que a probabilidade implícita mudou bruscamente (`|variação| >= 0.10`) **e** o volume do dia confirma liquidez (`>= US$ 10.000`), evitando falsos positivos por médias de preço instáveis em dias secos. Roda nos 4 mercados via `market_id IN (...)`.
- **`04_alerta2_volume_anomalo.sql`** — **Alerta 2**: sinaliza dias em que o volume surtou muito acima do normal (`>= 2,5x a média móvel de 7 dias`), com piso absoluto de `US$ 10.000` (metodologia Rolling Window). Roda nos mesmos 4 mercados.

Os dois alertas juntos somam mais de 70 linhas comentadas e retornam apenas os registros considerados relevantes pelas regras.

## Métrica de assertividade reprodutível

Diferente de uma abordagem baseada em lista fixa de datas de jogos, a assertividade usa um **"movimento estrutural real"** calculado a partir dos próprios dados: um dia conta como movimento real se o nível médio da probabilidade nos 3 dias seguintes difere do nível médio dos 3 dias anteriores em pelo menos 0,10. Isso captura reprecificações que se sustentam e ignora blips de um dia que revertem, e funciona em qualquer mercado, mesmo sem calendário de jogos.

O `relatorio.ipynb` reproduz as regras dos alertas em pandas por mercado (`groupby('market_id')`, thresholds expostos como variáveis), exibe o SQL como artefato, monta a tabela comparativa de precisão por time, faz uma varredura de parâmetros e visualiza os 4 mercados lado a lado.

## Como reproduzir

Os CSVs usados nesta análise estão disponíveis publicamente no Google Drive:

**Link do Drive:** https://drive.google.com/drive/folders/19AntdxijbWzIBn4rCDPNA4veYX_1riPm?usp=drive_link

Baixe os arquivos (`serie_multi.csv`, `volatilidade_multi.csv`, `mercados_multi.csv` — os CSVs da v1, `mercado.csv`/`serie_diaria.csv`/`volatilidade_diaria.csv`/`cobertura.csv`, também podem ficar na pasta) e coloque-os em `dados/` (pasta ignorada pelo git). O `relatorio.ipynb` lê apenas esses CSVs locais — nenhuma célula consulta o BigQuery ao vivo — e roda de ponta a ponta a partir daí.
