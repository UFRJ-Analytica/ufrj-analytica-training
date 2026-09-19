# Banco de Dados II — Entrega Individual

**Trainee:** Leticia Pessôa Machado

## Evento ou mercado escolhido

Mercados do **Polymarket** referentes à categoria **Best Picture** do Oscar, com foco na
98ª edição (Academy Awards 2026), analisados em relação às premiações precursoras que
antecedem a cerimônia: **Globo de Ouro**, **BAFTA**, **SAG/Actor Awards** e, quando
disponível, **Critics Choice Awards**.

Como estudo de caso comparativo, a 97ª edição (Academy Awards 2025, vencida por *Anora*)
também foi analisada — os mercados dessa temporada já estavam totalmente resolvidos e
tiveram uma janela de vida bem mais curta (~40 dias, contra ~170 dias na safra 2026), 
o que permitiu validar a metodologia contra um resultado real conhecido antes de aplicá-la
à safra 2026.


## Pergunta central

As premiações precursoras do Oscar (Globo de Ouro, BAFTA, SAG) fazem o mercado de Best
Picture do Polymarket se reprecificar de forma detectável logo após cada anúncio?

## Hipótese inicial

Grandes deslocamentos de preço (reprecificações abruptas da probabilidade implícita) não
ocorrem de forma linear ao longo da temporada, mas sim em saltos concentrados nas janelas
de tempo ao redor do anúncio de cada premiação precursora. Além disso, picos anômalos de
volume negociado antecedem ou acompanham diretamente esses saltos de preço.

## Tabelas e datasets utilizados no BigQuery

Projeto de treinamento: `even-continuity-441808-j0`

| Tabela | Uso |
|---|---|
| `polymarket_optimized.markets` | Metadados dos mercados (identificação de candidatos, categorias, datas de criação/encerramento, filtro de premiações precursoras via `event_title`) |
| `polymarket_mart.v_market_daily` | Baseline diário de preço e volume por mercado — fonte principal das análises de tendência e dos dois alertas, por ser tabela agregada de baixo custo |
| `polymarket_mart.daily_price_deviation` | Métricas de desvio e volatilidade diária já pré-calculadas — base do Alerta 2 |

## Período analisado

- **Safra 2025/2026** (candidato principal): mercados criados a partir de 26/09/2025,
  cobrindo a cerimônia de 15/03/2026.
- **Safra 2024/2025** (comparação/validação): mercados de 21/01/2025 a 02/03/2025
  (cerimônia do Oscar 2025).
- Datas-âncora das premiações precursoras usadas como marcos: Globo de Ouro (11/01/2026),
  BAFTA (22/02/2026), SAG/Actor Awards (01/03/2026), Oscar (15/03/2026) — e os equivalentes
  da safra 2025 (Critics Choice 07/02, PGA/DGA 08/02, WGA 15/02, BAFTA 16/02, SAG 23/02,
  Oscar 02/03).

## Descrição das consultas e dos alertas

**Exploração (Etapas 1-2):** mapeamento do universo de mercados do Oscar, identificação
dos dois formatos de mercado existentes (categoria única, contagem/agregado), e 
dimensionamento do total de mercados de categoria única disponíveis para análise 
(2.407 mercados, ~US$ 52,4 milhões de volume).

**Baseline e validação de qualidade do dado (Etapa 3):** série diária de preço e volume
por candidato, com auditoria de liquidez (correlação entre dias de preço extremo e baixa
contagem de negociações, usada como piso de confiança nos alertas) e checagem de lacunas
de calendário e do dia de liquidação pós-resolução, que precisa ser excluído para não
distorcer os cálculos de variação de preço.


**Alerta 1 — Salto de preço após bloco de premiações:** detecta automaticamente
agrupamentos de premiações próximas no calendário (técnica *gaps and islands*, sem datas
fixas digitadas manualmente) e mede a variação de preço médio nos 3 dias antes/depois de
cada bloco, exigindo também volume acima da média móvel recente. Retorna apenas os blocos
cuja variação e volume ultrapassam limiares definidos.

**Alerta 2 — Desvio estatístico (Z-score) com janela móvel:** calcula, para cada dia, um
Z-score da volatilidade de preço em relação à média/desvio-padrão dos 21 dias anteriores
(rolling window) — não depende de calendário de eventos nem de liquidez de mercados de
outras premiações, servindo como sinal independente de reprecificação anômala. Retorna
apenas os dias cujo desvio ultrapassa o limiar estatístico definido.

Os dois alertas foram desenhados como complementares: o Alerta 1 captura reações
direcionais e graduais (ex.: tendência de alta ao longo de vários dias após o BAFTA); o
Alerta 2 captura turbulência pontual de um único dia, mesmo sem relação direta com uma
data de premiação específica.

## Dados (CSVs)

Link público do Google Drive (permissão de leitura para "Qualquer pessoa com o link"):

https://drive.google.com/drive/folders/13ZtkCR1bnjuQIxX5xKytLJSpwG9AY0My?usp=sharing

O notebook `relatorio.ipynb` lê os arquivos localmente via `pd.read_csv('dados/arquivo.csv')`
— baixe a pasta do Drive acima e copie o conteúdo para `dados/` antes de reproduzir a análise.