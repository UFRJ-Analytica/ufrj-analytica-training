# Banco de Dados II - Análise de Dados Polymarket

## Objetivo
Realizar análise exploratória de dados de eventos Polymarket usando BigQuery como Data Warehouse.

## Estrutura
```
lucas_contreiras_trainee/
├── README.md (este arquivo)
├── queries.sql (consultas SQL no BigQuery)
└── Polymarket/
    └── relatorio_polymarket.ipynb (análise completa)
```

## Eventos Polymarket Analisados

### Event: Election Markets
- **Market Description**: Prediction markets para eventos políticos e eleitorais
- **Período**: 2024-2025
- **Tipo de Análise**: Tendências de preço, distribuição de participantes, volume de transações

## Dados
- **Projeto BigQuery**: even-continuity-441808-j0
- **Dataset**: polymarket_events
- **Fonte de Dados**: Polymarket Event API
- **CSV de Exportação**: [Link no Google Drive](https://drive.google.com/folder/id)

## Consultas SQL Principais

### Q1: Volume de Transações por Mercado
Agrega volume total de negócios por mercado, identificando os mais ativos.

### Q2: Distribuição de Preços ao Longo do Tempo
Análise de como os preços evoluem nos diferentes tipos de mercados.

### Q3: Ranking de Mercados por Liquidez
Identifica mercados com maior liquidez (volume * spread).

### Q4: Alerta 1 - Movimentos de Preço Anômalos
Detecta mudanças de preço superiores a X% em uma janela de tempo de Y horas.

### Q5: Alerta 2 - Volume Atípico
Identifica períodos com volume de transações acima de 2 desvios padrão.

## Análise no Notebook
- **Exploração**: Distribuição de dados, valores nulos, estatísticas básicas
- **Limpeza**: Tratamento de outliers, normalização de datas
- **Agregações**: Agrupamentos por tipo de mercado, período, liquidez
- **Visualizações**: Gráficos de série temporal, distribuições, correlações

## Como Executar

### 1. Configurar BigQuery
```bash
# Autenticar com Google Cloud
gcloud auth application-default login

# Definir projeto
gcloud config set project even-continuity-441808-j0
```

### 2. Rodar Queries no BigQuery
```sql
-- Executar em: https://console.cloud.google.com/bigquery
-- Dataset: polymarket_events
-- Copiar queries do arquivo queries.sql
```

### 3. Executar Notebook
```bash
jupyter notebook relatorio_polymarket.ipynb
```

## Requisitos
- BigQuery access (projeto even-continuity-441808-j0)
- Python 3.8+
- pandas, numpy, matplotlib, seaborn
- google-cloud-bigquery

## Instalação de Dependências
```bash
pip install google-cloud-bigquery pandas numpy matplotlib seaborn
```

## Validação da Entrega
- [x] Queries SQL criadas e validadas no BigQuery
- [x] Relatório Jupyter com análise exploratória
- [x] Alertas implementados e testados
- [x] Documentação completa

## Autor
Lucas Contreiras - UFRJ Analytica Training
Data: Julho 2026

## Referências
- [Polymarket API](https://polymarket.com)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [Google Cloud BigQuery Python Client](https://cloud.google.com/python/docs/reference/bigquery/latest)
