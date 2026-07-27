# Banco de Dados II
# Entrega: Polymarket no BigQuery

## Informações Gerais
* **Nome do Trainee:** Gabriel Siqueira Peroba
* **Evento/Mercado Escolhido:** Oscar 2024 - Melhor Atriz
* **Período Analisado:** 01 de Fevereiro de 2024 a 15 de Março de 2024.

## Contexto da Análise
* **Pergunta Central:** Como o mercado de predições reage e bota preços na probabilidade de vitória de candidatas ao Oscar durante a ocorrência de eventos do mundo real (como premiações prévias e a própria cerimônia)?
* **Hipótese Inicial:** A probabilidade não se altera de forma gradual no dia a dia. O mercado atua em um regime de degraus, onde os preços permanecem estáveis e sofrem quebras bruscas quando novas informações relevantes são consolidadas pelo público.

##  Dados e Metodologia
* **Tabelas utilizadas no BigQuery:**
  * `polymarket_optimized.markets`: Utilizada na etapa de exploração inicial para entender o esquema, mapear os metadados do evento e descobrir os respectivos `market_id` das indicadas.
  * `polymarket_optimized.trades`: Tabela transacional principal. Utilizada para construir agregações diárias do volume em dólares (`usd_amount`) e preço médio (`price`).

##  Descrição dos Arquivos SQL e Alerta Final
A lógica analítica foi construída de forma progressiva para mitigar altos custos computacionais no BigQuery, utilizando CTEs e filtros rigorosos de particionamento e clustering (IDs literais e janelas de data específicas).

* **Consultas de Exploração e Agregação:** Arquivos e queries dedicados ao mapeamento do terreno e consolidação de médias e somatórios diários por ativo.
* **Alerta Final Consolidado:** Uma consulta unificada (composta por múltiplas CTEs e `Window Functions`) responsável por implementar duas regras de monitoramento simultâneas:
  1. **Alerta de Choque de Preço:** Monitora a função `LAG()` para identificar e retornar apenas os registros onde ocorreu uma variação de probabilidade (salto ou queda) de **20% ou mais** em um intervalo de 24 horas.
  2. **Alerta de Pico de Volume:** Identifica dias de alta volatilidade financeira onde o volume transacionado foi superior ao triplo da média móvel calculada nos 3 dias imediatamente anteriores.

* **Tabelas utilizadas:** expploracao_inicial.csv, market_id_exploracao.csv, agregado.csv, consulta_final_alerta.csv

## 📁 Acesso aos Dados
* **Link da pasta `dados/` (Google Drive):** https://drive.google.com/drive/folders/1okZ-fQe4RMb26QkK-9Q0tQQQnUHwPjHG?usp=drive_link
