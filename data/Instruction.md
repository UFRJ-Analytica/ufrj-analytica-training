# Briefing de execução — Entrega Banco de Dados II (UFRJ Analytica)
### Mercado: "Will Aston Villa win the UEFA Champions League?" (Polymarket · BigQuery)

> **Como usar este arquivo:** abra o Claude Code na raiz do repositório da entrega e peça:
> *"Leia BRIEFING_CLAUDE_CODE.md e execute todas as tarefas da seção 5, respeitando as travas da seção 8."*
> Ele tem todo o contexto, os dados já coletados, o SQL pronto e a especificação do notebook. Você só precisa preencher o bloco CONFIG abaixo e, no fim, revisar e dar o `git push`.

---

## 0. CONFIG — preencher antes de rodar

```yaml
nome_trainee: "PREENCHER"          # vira a pasta entregaveis/banco_de_dados_2/<nome_trainee>/ e o slug
branch_individual: "PREENCHER"     # sua branch individual (NUNCA commitar direto na develop)
drive_link: "https://drive.google.com/drive/folders/19AntdxijbWzIBn4rCDPNA4veYX_1riPm?usp=drive_link"
market_id: "507286"
projeto_treinamento: "even-continuity-441808-j0"
```

---

## 1. O que é a entrega (contexto)

Análise de um mercado real do Polymarket usando SQL no BigQuery, entregue como um notebook Jupyter mais README, versionada no GitHub (branch individual → Pull Request para `develop`). A análise precisa investigar como o mercado se comportou **antes/durante/depois** de eventos relevantes, propor hipóteses, observar relações temporais e discutir limitações — **sem afirmar causalidade forte**. O núcleo técnico são **dois alertas em SQL** (juntos ≥ 70 linhas) que retornam **apenas os registros relevantes**.

**Fluxo de dados (já entendido):** o SQL roda no BigQuery a partir do projeto pessoal do trainee, referenciando as tabelas do projeto de treinamento pelo caminho completo entre crases. Os resultados são exportados como CSV para a pasta `dados/` (que o `.gitignore` bloqueia) e para o Google Drive. **O notebook NÃO consulta o BigQuery ao vivo** — ele lê os CSVs locais com `pd.read_csv('dados/...')`, para que o avaliador reproduza baixando os CSVs do Drive.

---

## 2. Tema, pergunta e hipótese

- **Mercado:** `Will Aston Villa win the UEFA Champions League?` — `market_id = 507286`, evento `Champions League Winner` (`event_id = 12585`, slug `champions-league-winner-2025`). Mercado **fechado** (`closed = 1`), criado em 2024-09-17, `end_date` 2025-05-31.
- **Pergunta central:** Como o volume negociado e a probabilidade implícita do mercado reagiram aos jogos do Aston Villa e à evolução do chaveamento ao longo da campanha 2024-25 da Champions League?
- **Hipótese inicial:** Os maiores saltos de probabilidade e os picos de volume se concentram em torno das datas de jogos do Villa e dos eventos de definição do mata-mata. Movimentos em dias de baixa liquidez são majoritariamente ruído, não reprecificação real.

---

## 3. Dados já coletados (estão em `dados/`)

Quatro CSVs já exportados do BigQuery pelo trainee. As queries que os geraram estão na seção 4 (devem ser salvas como arquivos `.sql`).

| Arquivo | Origem (tabela) | Colunas |
|---|---|---|
| `dados/mercado.csv` | `polymarket_optimized.markets` | market_id, question, event_title, event_id, event_slug, volume, created_at, end_date, closed, outcome_prices, token1, token2 |
| `dados/cobertura.csv` | `polymarket_mart.daily_market_stats` | primeiro_dia, ultimo_dia, dias_com_dados, volume_total |
| `dados/serie_diaria.csv` | `polymarket_mart.v_market_daily` | trade_date, avg_trade_price, min_trade_price, max_trade_price, daily_trade_count, daily_usd_volume, rolling_7d_avg_volume |
| `dados/volatilidade_diaria.csv` | `polymarket_mart.v_price_quality_daily` | trade_date, price_volatility, avg_price_deviation, max_price_deviation, matched_trades, rolling_7d_avg_deviation |

**Fatos-chave já extraídos dos dados (use na narrativa, não precisa recalcular do zero):**
- Período coberto: **2024-09-17 a 2025-04-15 (211 dias)**. Os dados terminam no dia da eliminação (jogo de volta vs PSG, 15/04/2025).
- `avg_trade_price` funciona como **probabilidade implícita** (0 a 1) do Villa ser campeão. **Atenção:** é uma média simples dos preços negociados no dia; em dias de baixa liquidez ela oscila muito (ruído). Documente isso como limitação.
- `daily_usd_volume` somado no período ≈ US$ 5,29 mi (volume casado no mart); o campo `volume` da tabela `markets` (~US$ 133 mi) é o volume nocional/lifetime reportado pelo Polymarket — métricas diferentes, não confundir.
- Probabilidade: mín ≈ 0,012, máx ≈ 0,791; começa ~0,02, termina ~0,11 (Villa não avançou às semis).
- **Anomalia a discutir:** o maior volume isolado, **2024-10-30 (~US$ 689 mil, probabilidade saltando para ~0,55)**, NÃO coincide com jogo do Villa. Provável posição grande / ruído — tratar como limitação, não como sinal.

---

## 4. Arquivos SQL a criar (em `sql/`)

Salvar cada query como arquivo comentado. Todas referenciam o caminho completo com crases e evitam `SELECT *`.

**`sql/01_exploracao.sql`** — as 4 queries de exploração/coleta (as que geraram os CSVs da seção 3). Incluir as quatro, cada uma com um comentário de cabeçalho explicando a pergunta. Modelo da principal:

```sql
-- Exploração: metadados do mercado escolhido
SELECT market_id, question, event_title, event_id, event_slug,
       volume, created_at, end_date, closed, outcome_prices, token1, token2
FROM `even-continuity-441808-j0.polymarket_optimized.markets`
WHERE market_id = '507286';

-- Cobertura temporal do mercado (define a janela da análise)
SELECT MIN(trade_date) AS primeiro_dia, MAX(trade_date) AS ultimo_dia,
       COUNT(*) AS dias_com_dados, SUM(daily_usd_volume) AS volume_total
FROM `even-continuity-441808-j0.polymarket_mart.daily_market_stats`
WHERE market_id = '507286';

-- Série diária: probabilidade implícita, volume e média móvel de 7 dias
SELECT trade_date, avg_trade_price, min_trade_price, max_trade_price,
       daily_trade_count, daily_usd_volume, rolling_7d_avg_volume
FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
WHERE market_id = '507286'
ORDER BY trade_date;

-- Volatilidade / qualidade de preço diária
SELECT trade_date, price_volatility, avg_price_deviation, max_price_deviation,
       matched_trades, rolling_7d_avg_deviation
FROM `even-continuity-441808-j0.polymarket_mart.v_price_quality_daily`
WHERE market_id = '507286'
ORDER BY trade_date;
```

**`sql/02_agregacoes.sql`** — consulta analítica que deriva a variação diária de probabilidade (via `LAG` numa CTE) e a razão volume/média-móvel, base para os alertas. Comentar a lógica de otimização (uso das tabelas de mart agregadas em vez da `trades`; funções de janela declaradas em CTE, não inline).

```sql
-- Agregação analítica: variação diária de probabilidade e razão de volume
-- Otimização: usamos a view agregada v_market_daily (processa MB, não GB) e
-- declaramos as funções de janela numa CTE para filtrar com WHERE simples.
WITH serie AS (
  SELECT
    market_id,
    trade_date,
    avg_trade_price                                   AS probabilidade,
    LAG(avg_trade_price) OVER (
      PARTITION BY market_id ORDER BY trade_date)     AS probabilidade_anterior,
    daily_usd_volume                                  AS volume_dia,
    rolling_7d_avg_volume                             AS volume_medio_7d,
    daily_trade_count                                 AS trades_dia
  FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
  WHERE market_id = '507286'
)
SELECT
  market_id,
  trade_date,
  probabilidade,
  ROUND(probabilidade - probabilidade_anterior, 4)          AS variacao_probabilidade,
  volume_dia,
  volume_medio_7d,
  ROUND(SAFE_DIVIDE(volume_dia, volume_medio_7d), 2)        AS razao_volume,
  trades_dia
FROM serie
WHERE probabilidade_anterior IS NOT NULL
ORDER BY trade_date;
```

**`sql/03_alerta1_salto_probabilidade.sql`** e **`sql/04_alerta2_volume_anomalo.sql`** — os dois alertas (SQL completo na seção 6). Juntos passam de 70 linhas com os comentários.

---

## 5. Tarefas do Claude Code (execute nesta ordem)

1. **Criar a estrutura de pastas** (usar `nome_trainee` do CONFIG):
   ```
   entregaveis/banco_de_dados_2/<nome_trainee>/
     README.md
     relatorio.ipynb
     sql/
       01_exploracao.sql
       02_agregacoes.sql
       03_alerta1_salto_probabilidade.sql
       04_alerta2_volume_anomalo.sql
     dados/            # os 4 CSVs já estão aqui; NÃO versionar
   ```
2. **Escrever os 4 arquivos `.sql`** conforme seções 4 e 6, todos comentados.
3. **Escrever o `relatorio.ipynb`** conforme a especificação da seção 7. Ele deve rodar de ponta a ponta lendo só os CSVs de `dados/` (nenhuma chamada ao BigQuery).
4. **Escrever o `README.md`** conforme a seção 9.
5. **Conferir o `.gitignore`** da raiz do repo: garantir que `*.csv` (ou `dados/`) está ignorado. Se não estiver, adicionar. Nunca forçar `git add` de CSV.
6. **Preparar o commit** (seção 10) e **parar antes do `git push`** — push e Pull Request são do trainee (ver travas na seção 8).

---

## 6. Os dois alertas (SQL pronto e calibrado)

Thresholds calibrados a partir da série real. Rodando essas regras sobre `serie_diaria.csv`: **Alerta 1 → 12 disparos; Alerta 2 → 19 disparos** (útil pra métrica de assertividade). Os thresholds ficam expostos como variáveis no notebook para permitir tuning.

### `sql/03_alerta1_salto_probabilidade.sql`
```sql
-- ============================================================================
-- ALERTA 1 — Salto de probabilidade confirmado por liquidez
-- Pergunta: em quais dias a probabilidade implícita mudou bruscamente de forma
-- confiável (não por ruído de dia seco)?
-- Regra: |variação da probabilidade dia-a-dia| >= 0.10  E  volume do dia >= 10.000 USD.
-- A trava de volume evita disparos falsos causados por médias de preço instáveis
-- em dias de baixíssima liquidez (ex.: probabilidade "0,79" movida por ~US$186).
-- Otimização: view agregada v_market_daily; LAG declarado em CTE; filtro em WHERE.
-- ============================================================================
WITH serie AS (
  SELECT
    market_id,
    trade_date,
    avg_trade_price                                   AS probabilidade_atual,
    LAG(avg_trade_price) OVER (
      PARTITION BY market_id ORDER BY trade_date)     AS probabilidade_anterior,
    daily_usd_volume                                  AS volume_atual,
    rolling_7d_avg_volume                             AS volume_medio_7d,
    daily_trade_count                                 AS trades_dia
  FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
  WHERE market_id = '507286'
),
com_variacao AS (
  SELECT
    *,
    ROUND(probabilidade_atual - probabilidade_anterior, 4) AS variacao_probabilidade,
    ABS(probabilidade_atual - probabilidade_anterior)      AS variacao_abs
  FROM serie
  WHERE probabilidade_anterior IS NOT NULL
)
SELECT
  market_id,
  trade_date,
  probabilidade_anterior,
  probabilidade_atual,
  variacao_probabilidade,
  volume_atual,
  volume_medio_7d,
  trades_dia,
  'salto_probabilidade' AS tipo_alerta
FROM com_variacao
WHERE variacao_abs >= 0.10        -- salto relevante de probabilidade
  AND volume_atual  >= 10000      -- confirmação de liquidez
ORDER BY variacao_abs DESC;
```

### `sql/04_alerta2_volume_anomalo.sql`
```sql
-- ============================================================================
-- ALERTA 2 — Volume anômalo (Rolling Window de 7 dias)
-- Pergunta: em quais dias a atividade de negociação surtou muito acima do normal?
-- Regra: volume do dia >= 2.5x a média móvel de 7 dias  E  >= 10.000 USD.
-- O piso absoluto evita disparos em dias iniciais com média móvel minúscula.
-- Metodologia: Rolling Window (rolling_7d_avg_volume já vem calculada na view).
-- Sinaliza surtos tipicamente associados a jogos e à definição do chaveamento.
-- ============================================================================
WITH serie AS (
  SELECT
    market_id,
    trade_date,
    avg_trade_price                                   AS probabilidade_atual,
    daily_usd_volume                                  AS volume_atual,
    rolling_7d_avg_volume                             AS volume_medio_7d,
    daily_trade_count                                 AS trades_dia,
    SAFE_DIVIDE(daily_usd_volume, rolling_7d_avg_volume) AS razao_vol
  FROM `even-continuity-441808-j0.polymarket_mart.v_market_daily`
  WHERE market_id = '507286'
)
SELECT
  market_id,
  trade_date,
  probabilidade_atual,
  volume_atual,
  volume_medio_7d,
  ROUND(razao_vol, 2) AS razao_vol_sobre_media,
  trades_dia,
  'volume_anomalo' AS tipo_alerta
FROM serie
WHERE razao_vol    >= 2.5         -- volume >= 2,5x a média móvel de 7 dias
  AND volume_atual >= 10000       -- piso absoluto de liquidez
ORDER BY razao_vol DESC;
```

---

## 7. Especificação do `relatorio.ipynb`

O notebook deve ler **apenas** os CSVs de `dados/` e rodar de ponta a ponta. Reproduzir as regras dos alertas em pandas (a partir de `serie_diaria.csv`) para gerar visualização e métricas — mostrando também o SQL como artefato. Células, na ordem:

1. **[Markdown] Cabeçalho** — título, evento escolhido, pergunta de pesquisa e hipótese inicial (seção 2).
2. **[Code] Setup** — `import pandas as pd, numpy as np, matplotlib.pyplot as plt`. Ler os 4 CSVs; `parse_dates=['trade_date']` na série e na volatilidade; ordenar por data.
3. **[Markdown+Code] Exploração inicial** — mostrar as queries (seção 4) como texto, o `head()` dos CSVs e o período/cobertura. Explicar por que este mercado foi escolhido (volume alto, fechado, evento com datas claras).
4. **[Markdown+Code] Agregações** — a partir de `serie_diaria.csv`, calcular `variacao_probabilidade = avg_trade_price.diff()` e `razao_volume = daily_usd_volume / rolling_7d_avg_volume`. Fazer merge com `volatilidade_diaria.csv` por `trade_date`. Mostrar o SQL de `02_agregacoes.sql` como referência e comentar a lógica de otimização (mart agregado, `LAG`/janela em CTE, datas literais, sem `SELECT *`).
5. **[Markdown+Code] Dois alertas** — exibir o SQL dos dois alertas (seções 6) e reproduzir as regras em pandas, expondo os thresholds como variáveis:
   ```python
   LIMIAR_SALTO_PROB = 0.10
   PISO_VOLUME       = 10000
   RAZAO_VOLUME      = 2.5

   df['variacao_prob'] = df['avg_trade_price'].diff()
   alerta1 = df[(df['variacao_prob'].abs() >= LIMIAR_SALTO_PROB) &
                (df['daily_usd_volume'] >= PISO_VOLUME)].copy()

   df['razao_vol'] = df['daily_usd_volume'] / df['rolling_7d_avg_volume']
   alerta2 = df[(df['razao_vol'] >= RAZAO_VOLUME) &
                (df['daily_usd_volume'] >= PISO_VOLUME)].copy()
   ```
   (Opcional: se `dados/alerta1.csv`/`dados/alerta2.csv` existirem — exportados do BigQuery — carregá-los e conferir que batem com a reprodução em pandas, como evidência de que o SQL roda no BQ.)
6. **[Markdown+Code] Demonstração + assertividade** — gráfico matplotlib com dois eixos: linha da probabilidade (`avg_trade_price`) e barras/linha do volume diário, ao longo do tempo; marcar os disparos do Alerta 1 e do Alerta 2 (ex.: `scatter`/linhas verticais) e sobrepor as **datas de eventos reais** (seção 8-A). Calcular a **assertividade (precisão)** de cada alerta: fração dos disparos que caem a ≤ 1 dia de uma data de evento real. Usar a lista `DATAS_EVENTOS` da seção 8-A:
   ```python
   from datetime import timedelta
   eventos = pd.to_datetime(DATAS_EVENTOS)
   def casa(data, janela=1):
       return any(abs((data - e).days) <= janela for e in eventos)
   for nome, al in [('Alerta 1', alerta1), ('Alerta 2', alerta2)]:
       casados = al['trade_date'].apply(casa).sum()
       total = len(al)
       print(f'{nome}: precisão = {casados}/{total} = {casados/total:.0%}')
   ```
   Comentar o resultado: disparos que NÃO casam (ex.: 30/10/2024) são candidatos a ruído/posição grande, não a movimento fundamentado.
7. **[Markdown] Observações, inferências e limitações** — separar claramente: (a) o que os dados mostram; (b) hipóteses; (c) limitações. Limitações a citar: `avg_trade_price` é média simples e instável em dias secos; possível mistura de tokens de outcome (min≈0/max≈1 no mesmo dia); a anomalia de 30/10; dados terminam na eliminação (15/04); **sem afirmações de causalidade** — apenas coincidência temporal.

---

## 8. Materiais de apoio e travas

### 8-A. Datas de eventos reais (Villa na Champions 2024-25) — para a assertividade
Fonte: calendário oficial da UEFA. Fase de liga = jogos do Villa; playoff = reshuffle do chaveamento (o Villa não jogou, mas o mercado reprecificou). Colar no notebook:
```python
DATAS_EVENTOS = [
    "2024-09-17",  # Young Boys 0-3 Villa (liga)
    "2024-10-02",  # Villa 1-0 Bayern (liga)
    "2024-10-22",  # Villa 2-0 Bologna (liga)
    "2024-11-06",  # Club Brugge 1-0 Villa (liga)
    "2024-11-27",  # Villa 0-0 Juventus (liga)
    "2024-12-10",  # Leipzig 2-3 Villa (liga)
    "2025-01-21",  # Monaco 1-0 Villa (liga)
    "2025-01-29",  # Villa 4-2 Celtic (liga; Villa se classifica em 8º)
    "2025-02-11", "2025-02-12",  # playoff do mata-mata (reshuffle)
    "2025-02-18", "2025-02-19",  # playoff do mata-mata (reshuffle)
    "2025-03-04", "2025-03-05",  # oitavas ida (Villa vs Club Brugge)
    "2025-03-11", "2025-03-12",  # oitavas volta (Villa 6-1 agg)
    "2025-04-09",  # quartas ida: PSG 3-1 Villa
    "2025-04-15",  # quartas volta: Villa 3-2 PSG (eliminado 4-5 agg)
]
```
Nota metodológica para o texto: usa-se janela de ±1 dia porque o mercado se move na véspera (escalações/notícias) e no dia seguinte (liquidação). A janela é uma escolha do analista, não verdade absoluta — declarar como limitação.

### 8-B. Regras de otimização do BigQuery (repetir nos comentários dos `.sql`)
Sem `SELECT *`; `LIMIT` só para inspeção; datas **literais** fixas (nunca `CURRENT_DATE()`), para aproveitar o cache; preferir tabelas de mart agregadas; na `trades` (não usada aqui) sempre filtrar `DATE(trade_timestamp)` + `market_id` e usar `OR` de intervalos curtos em vez de `BETWEEN` largo; funções de janela em CTE, não inline.

### 8-C. Travas (o Claude Code NÃO deve fazer sozinho)
- **NÃO** rodar `git push` nem abrir Pull Request — são ações de publicação, ficam com o trainee após revisão.
- **NÃO** commitar arquivos `.csv`, credenciais ou tokens.
- **NÃO** commitar na branch `develop` — apenas na branch individual do CONFIG.
- **NÃO** consultar o BigQuery a partir do notebook — só ler CSVs de `dados/`.

---

## 9. Conteúdo do `README.md`
Deve conter, nesta ordem: nome do trainee; evento/mercado escolhido (Will Aston Villa win the UEFA Champions League?, `market_id 507286`); pergunta central (seção 2); hipótese inicial (seção 2); tabelas/datasets usados (`polymarket_optimized.markets`, `polymarket_mart.v_market_daily`, `polymarket_mart.daily_market_stats`, `polymarket_mart.v_price_quality_daily`); período analisado (2024-09-17 a 2025-04-15); descrição breve dos arquivos SQL e dos dois alertas (regra + o que cada um retorna); e o **link público do Google Drive** (`drive_link` do CONFIG) com nota de que os CSVs devem ser baixados para `dados/` para reproduzir o notebook. Incluir uma linha explicando a estrutura de pastas.

---

## 10. Git (revisar e executar por último — trainee dá o push)
```bash
git status                      # confirmar que está na branch individual, NÃO na develop
git add entregaveis/banco_de_dados_2/<nome_trainee>/
git status                      # conferir que NENHUM .csv entrou no stage
git commit -m "Finaliza entrega de Banco de Dados II"
# --- daqui em diante é o trainee, após revisar tudo: ---
git push
# abrir Pull Request da branch individual -> develop
```

---

## 11. Passo manual que sobra para o trainee (opcional, evidência extra)
No BigQuery (projeto pessoal ativo), rodar `sql/03_alerta1_salto_probabilidade.sql` e `sql/04_alerta2_volume_anomalo.sql`, exportar cada resultado como `dados/alerta1.csv` e `dados/alerta2.csv` e subir ao Drive. O notebook já reproduz os alertas em pandas, então isso é só evidência adicional de que o SQL roda no BigQuery — não é obrigatório para o notebook funcionar.