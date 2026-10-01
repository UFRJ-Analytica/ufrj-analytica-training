# Banco de Dados II – Projeto Final

## Análise de Mercados da Polymarket utilizando BigQuery

### Autor

Diogo Vieira

---

# Objetivo

O projeto teve como objetivo desenvolver alertas estatísticos para identificar comportamentos anômalos em mercados da plataforma Polymarket utilizando consultas SQL no Google BigQuery.

Inicialmente, a análise foi conduzida sobre o mercado:

- **Will Bitcoin reach $1,000,000 by December 31, 2025?**

Entretanto, durante o desenvolvimento observou-se que esse mercado, por representar apenas um contrato específico, limitava a capacidade de generalização dos alertas. Dessa forma, a análise foi expandida para abranger todos os mercados pertencentes aos eventos:

- **What price will Bitcoin hit in 2025?**
- **What price will Bitcoin hit in 2026?**

Totalizando **55 mercados (market_id)** analisados.

Essa mudança tornou os alertas mais genéricos e reutilizáveis, permitindo avaliar seu comportamento em diversos mercados relacionados ao preço do Bitcoin.

---

# Pergunta de pesquisa

É possível identificar automaticamente comportamentos anômalos nos mercados de previsão utilizando apenas informações históricas de volume e preço das negociações?

---

# Hipótese

Mercados que apresentam aumentos incomuns no volume negociado tendem também a apresentar oscilações anormais no preço médio das negociações. Esses comportamentos podem ser detectados utilizando métricas estatísticas calculadas por meio de funções analíticas do SQL.

---

# Base de dados

As consultas foram realizadas no conjunto de dados disponibilizado pela disciplina no Google BigQuery.

Tabela principal utilizada:

- `v_market_daily`

Além da exploração inicial dos mercados para seleção dos eventos de Bitcoin.

---

# Organização do notebook

O notebook está dividido nas seguintes etapas:

1. Introdução
2. Exploração dos dados
3. Consultas analíticas
4. Desenvolvimento dos alertas e comparação
5. Conclusão

---

# Alertas desenvolvidos

## Alerta 1 — Volume Anômalo

Detecta dias em que o volume financeiro negociado é significativamente superior ao comportamento recente do próprio mercado.

Para isso foram utilizados:

- média móvel de 7 dias;
- desvio padrão móvel;
- razão entre volume atual e média histórica;
- Score Z.

Os resultados são classificados em:

- Moderado
- Alto
- Crítico

---

## Alerta 2 — Variação Anômala de Preço

Detecta mudanças incomuns no preço médio diário (`avg_trade_price`).

O alerta utiliza:

- variação percentual diária;
- média móvel;
- desvio padrão móvel;
- Score Z.

Os registros também são classificados em:

- Moderado
- Alto
- Crítico

Além de métricas de:

- Alta
- Queda

---

# Principais resultados

A análise mostrou que:

- os mercados pertencentes ao evento **"What price will Bitcoin hit in 2025?"** concentraram maior quantidade de alertas do que os mercados equivalentes de 2026;

- os dois alertas apresentaram comportamento semelhante, destacando praticamente os mesmos mercados como concentradores de atividade anômala;

- a comparação entre os alertas, por meio de gráficos de barras, gráfico de dispersão e coeficiente de correlação, indicou uma forte associação positiva entre a quantidade de alertas de volume e de preço por mercado.

Esses resultados sugerem que mercados com maior atividade de negociação também tendem a apresentar maiores oscilações no preço médio, reforçando a consistência dos dois métodos de detecção.

---

# Dados

Os arquivos CSV utilizados pelo notebook estão disponíveis na pasta compartilhada do Google Drive:

**Link da pasta:**

> https://drive.google.com/drive/folders/1GyE4QDXN2MnsuTIkPHm6Vd2D_9BbJz4_?usp=sharing