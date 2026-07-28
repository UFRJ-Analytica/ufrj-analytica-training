# Banco de Dados II — Análise de mercado do Polymarket 

## Nome

Pedro Henrique Ferrari 

## Sobre a análise

Este trabalho analisa um mercado do Polymarket relacionado à classificação do Sacramento Kings para os playoffs da NBA.

Período analisado: 31/01/2025 a 19/04/2025

## Pergunta de pesquisa

Como o volume e o preço médio mudaram ao longo do período e em quais registros ocorreram movimentos fora do padrão recente?

## Hipótese inicial

A expectativa era encontrar registros em que o volume ou a variação do preço ficassem bem acima do padrão recente.

Depois da análise inicial do Sacramento Kings, as mesmas regras foram aplicadas a outros mercados para verificar se os alertas também funcionavam fora do caso original.

## Mercados analisados

- Sacramento Kings;
- Boston Celtics;
- Los Angeles Lakers;
- Phoenix Suns;
- Milwaukee Bucks.

## Dados utilizados

As consultas foram executadas no BigQuery utilizando as seguintes tabelas:

- `even-continuity-441808-j0.polymarket_optimized.markets`
- `even-continuity-441808-j0.polymarket_mart.daily_market_stats`

A primeira tabela foi utilizada para localizar os mercados e obter suas informações gerais.

A segunda tabela foi utilizada para recuperar o histórico diário de volume negociado e preço médio.

### Alerta 1 — Volume acima da média recente

O primeiro alerta compara o volume atual com a média de até sete registros anteriores do mesmo mercado.

O alerta exige pelo menos três observações anteriores e dispara quando o volume atual é pelo menos 2,5 vezes a média recente.

### Alerta 2 — Mudança brusca no preço médio

O segundo alerta compara o preço médio atual com o preço do registro anterior do mesmo mercado.

O alerta dispara quando a diferença absoluta entre os dois preços é maior ou igual a 0,10.

As consultas completas dos dois alertas estão disponíveis dentro do arquivo `relatorio.ipynb`.

## Resultados

O alerta de volume gerou 44 disparos. Entre os 41 alertas que possuíam um registro posterior, 21 foram confirmados, resultando em uma assertividade de 51,22%.

O alerta de preço gerou 133 disparos. Entre os 129 alertas que possuíam um registro posterior, 30 foram confirmados, resultando em uma assertividade de 23,26%.

O alerta de volume apresentou maior proporção de confirmações. O alerta de preço disparou mais vezes, mas apresentou menor continuidade no registro seguinte.

As duas regras dispararam em mercados diferentes e puderam ser aplicadas sem alteração dos parâmetros.

## Dados no Google Drive

https://drive.google.com/drive/folders/1pl45WbRIkanomrS3ArIxOKsxWhVghBlW?usp=sharing

## Estrutura 

```text
pedro-henrique-ferrari/
├── README.md
├── relatorio.ipynb
└── dados/
    ├── 01_mercado_escolhido.csv
    ├── 02_historico_diario.csv
    ├── 04_metricas_mercados_nba.csv
    ├── 05_alerta_volume_nba.csv
    └── 06_alerta_preco_nba.csv

```