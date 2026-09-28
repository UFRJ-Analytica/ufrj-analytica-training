# Entrega — Banco de Dados II · Polymarket no BigQuery

- **Trainee:** `Júlia Vilela`

- **Evento / mercado escolhido:** Mercado *"Biden drops out"* do Polymarket (`market_id 252294`),
  analisado em torno do primeiro debate presidencial Biden × Trump (27/06/2024) e do anúncio de
  desistência de Biden (21/07/2024). Outcome analisado: token **YES**
  (`asset_id 80466862227762400456474037114326989569691448086113369690204721936360568404468`).

- **Pergunta central:** O mercado precificou a saída de Biden de forma **gradual** após o debate, ou
  reagiu de forma **concentrada** em poucos momentos (o debate e o anúncio)? O volume anômalo
  **antecede** ou **acompanha** os movimentos de probabilidade implícita?

- **Hipótese inicial:** O debate provoca salto imediato de probabilidade; segue-se deriva ascendente
  com volume elevado; o anúncio de 21/07 é o maior choque de volume, mas com pouco movimento de preço
  restante (o mercado já teria precificado quase tudo).

- **Tabelas / datasets utilizados no BigQuery:**
  - `even-continuity-441808-j0.polymarket_optimized.markets` — seleção do mercado.
  - `even-continuity-441808-j0.polymarket_optimized.trades` — trades transacionais (grão fino);
    particionada por `DATE(trade_timestamp)`, clusterizada por `market_id`.
  - `even-continuity-441808-j0.polymarket_mart.daily_market_stats` — contexto diário (baixo custo);
    colunas usadas: `market_id, event_title, trade_date, daily_trade_count, daily_usd_volume,
    avg_trade_price, min_trade_price, max_trade_price`.

- **Período analisado:** 24/06/2024 a 24/07/2024 (baseline antes do debate + janela da desistência).

- **Arquivos e organização da entrega:**
  - `relatorio.ipynb` — Contém, em cada seção, o **código SQL** das consultas executadas no BigQuery (como strings, para documentação e reprodutibilidade) junto ao
    texto explicativo, aos dados carregados e às visualizações. É nele que residem as duas queries de
    alerta; não há arquivos `.sql` avulsos na entrega.
  - `dados/` — pasta local com apenas os **CSVs** exportados do BigQuery, que o notebook importa via
    `pd.read_csv('dados/...')`. Os arquivos (disponibilizados via Google Drive) são:
    - `01_exploracao_mercados.csv` — mercados retornados na busca (seleção do mercado analisado).
    - `01b_trajetoria_outcomes.csv` — trajetória diária de preço por outcome (identificação do YES).
    - `02_daily_market_stats.csv` — contexto diário agregado do mercado (tabela de mart).
    - `03_features_horarias.csv` — features horárias (volume, VWAP, traders, imbalance).
    - `04_alerta1.csv` — disparos do Alerta 1 (anomalia de volume, score Z).
    - `05_alerta2.csv` — disparos do Alerta 2 (cruzamento de médias móveis).

- **Descrição dos dois alertas:**
  - **Alerta 1 — score Z de volume:** sinaliza horas com volume ≥ 3 desvios acima da média causal de
    24h **e** ≥ 5 traders distintos (movimento atípico e distribuído).
  - **Alerta 2 — Rolling Windows:** sinaliza cruzamentos da média móvel curta (3h) com a longa (12h) da
    probabilidade implícita (mudança de tendência).

- **Link do Google Drive com a pasta `dados/`:** `https://drive.google.com/drive/folders/1l4TltqPYt85RvhHxg91ZtDQBbGPzj0r3?usp=sharing`
  *

---

## Como reproduzir
1. Baixe os CSVs do Drive para `entregaveis/banco_de_dados_2/nome_trainee/dados/`.
2. Abra `relatorio.ipynb` e execute as células (ele lê apenas de `dados/`).
