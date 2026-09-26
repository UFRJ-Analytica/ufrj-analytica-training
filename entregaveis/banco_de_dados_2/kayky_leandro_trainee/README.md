# Análise Exploratória dos Mercados de Apostas da UEFA Champions League no Polymarket

## Sobre o projeto

Este projeto foi desenvolvido como parte da atividade de Banco de Dados II da Liga Analytica (UFRJ).

O objetivo foi realizar uma Análise Exploratória de Dados (EDA) utilizando informações públicas do Polymarket, aplicando consultas SQL no Google BigQuery e posteriormente realizando o tratamento, exploração e visualização dos dados em Python através do Google Colab.

---

# Evento analisado

**UEFA Champions League**

Foram analisados exclusivamente os mercados relacionados à Champions League presentes na base de dados do Polymarket.

---

# Pergunta de pesquisa

**Quais padrões podem ser identificados nos mercados de apostas da UEFA Champions League e quais mercados merecem atenção por apresentarem elevado volume de negociação ou proximidade do encerramento?**

---

# Hipótese

Os mercados da Champions League concentram grande volume financeiro em poucos eventos específicos, principalmente partidas mais relevantes da competição. Além disso, mercados próximos do encerramento tendem a apresentar maior atividade dos usuários.

---

# Tabelas utilizadas

Durante a construção da análise foram utilizadas as seguintes tabelas disponibilizadas no BigQuery:

- markets
- events
- tokens

Além dessas tabelas, foram utilizados arquivos CSV exportados das consultas SQL para realização da análise exploratória no Google Colab.

---

# Etapas realizadas

O projeto foi desenvolvido nas seguintes etapas:

- Definição do tema da análise;
- Construção das consultas SQL no BigQuery;
- Exportação das consultas em formato CSV;
- Limpeza e tratamento dos dados com Pandas;
- Análise exploratória dos dados (EDA);
- Criação de visualizações utilizando Matplotlib;
- Desenvolvimento de dois alertas analíticos em SQL;
- Avaliação dos resultados encontrados.

---

# Alerta 1

### Mercados com maior volume financeiro

Este alerta identifica mercados que apresentam alto volume de negociação.

Objetivo:

- identificar eventos de maior interesse;
- encontrar mercados com elevada liquidez;
- destacar oportunidades para acompanhamento.

---

# Alerta 2

### Mercados próximos do encerramento com alto volume

Este alerta identifica mercados que estão próximos do fechamento e que apresentam elevado volume financeiro.

Objetivo:

- monitorar mercados em fase final;
- identificar concentração de negociações próximo ao encerramento;
- destacar eventos que podem demandar maior atenção.

---

# Principais resultados

A análise mostrou que:

- poucos mercados concentram grande parte do volume negociado;
- existem categorias de apostas significativamente mais populares;
- mercados próximos do encerramento apresentam intensa movimentação financeira;
- os alertas permitem identificar automaticamente mercados relevantes para monitoramento.

---

# Tecnologias utilizadas

- Google BigQuery
- SQL
- Google Colab
- Python
- Pandas
- Matplotlib

---

# Estrutura do projeto

```
dados/
│
├── *.csv

relatorio.ipynb

README.md
```

Os arquivos CSV **não são versionados** no GitHub e devem ser armazenados localmente na pasta `dados/`.

---

# Google Drive

Os arquivos CSV utilizados na análise podem ser acessados através do link abaixo:

https://drive.google.com/drive/folders/1VtJb44TBPERVC2XAt2laAwcrHsGRJYVZ?usp=sharing

---

# Como executar

1. Baixe os arquivos CSV disponíveis no Google Drive;
2. Crie uma pasta chamada `dados/`;
3. Coloque todos os CSVs dentro dessa pasta;
4. Abra o arquivo `relatorio.ipynb`;
5. Execute todas as células do notebook.

---

# Autor

**Kayky Leandro**

Liga Analytica — UFRJ

Banco de Dados II