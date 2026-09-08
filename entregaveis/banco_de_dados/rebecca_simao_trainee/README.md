# Entrega Banco de Dados I — Rebecca Simão

## Objetivo

O objetivo do trabalho foi montar um banco de dados com informações do IBGE sobre regiões, estados, municípios e população.

Durante a atividade, foram criadas as tabelas, definidos os relacionamentos entre elas e feitas consultas para conferir e analisar os dados.

## Arquivos

- `database.db`: banco de dados;
- `schema.sql`: criação das tabelas;
- `carga.sql`: inserção dos dados;
- `queries.sql`: consultas de conferência;
- `analytics.sql`: consultas de análise;
- `modelo_logico.png`: modelo do banco;
- `README.md`: informações sobre a entrega.

## Organização do banco

Os dados foram coletados de fontes públicas do IBGE com o uso de Python e depois importados para o SQLite.

O banco foi dividido em quatro tabelas principais:

### `regioes`

Contém o código, a sigla e o nome das regiões.

### `estados`

Contém os estados e a região de cada um.

### `municipios`

Contém os municípios e o estado ao qual pertencem.

### `populacao_municipal`

Contém os dados de população dos municípios, como ano, indicador, valor, unidade e fonte.

Nessa tabela, a chave é formada por `id_municipio`, `ano` e `indicador`, porque um mesmo município pode ter mais de um registro.

## Relacionamentos

```text
regioes
   ↓
estados
   ↓
municipios
   ↓
populacao_municipal
```

As tabelas foram criadas e preenchidas nessa ordem por causa dos relacionamentos entre elas.

## Consultas

No arquivo `queries.sql`, foram feitas consultas para visualizar os dados e conferir se as tabelas estavam relacionadas corretamente.

No arquivo `analytics.sql`, foram feitas análises como população por região, municípios mais populosos, médias e divisão dos municípios por faixa de população.
