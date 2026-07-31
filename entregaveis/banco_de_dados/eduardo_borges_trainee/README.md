# Entrega Banco de Dados 1 - eduardo_borges

# Projeto de Banco de Dados I - UFRJ Analytica

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado para responder a perguntas de negócio e análises populacionais de forma eficiente e sem redundância de dados.

## Arquivos da entrega

- `database.db`: Banco SQLite contendo tanto as tabelas brutas preservadas quanto as tabelas finais normalizadas.
- `schema.sql`: Script de criação das tabelas e definição das restrições (chaves primárias e estrangeiras).
- `carga.sql`: Script de migração e população das tabelas finais a partir dos dados brutos.
- `queries.sql`: Consultas SQL obrigatórias de exploração, validação e testes estruturais.
- `analytics.sql`: Consultas focadas em análise de dados (rankings, distribuições e classificações).
- `modelo_logico.png`: Diagrama do modelo lógico gerado a partir do banco de dados.

## Dados Brutos

As tabelas com prefixo `raw_` (`raw_regioes`, `raw_estados`, `raw_municipios`, `raw_populacao_municipal` e a tabela combinada `raw_municipios_com_populacao`) foram mantidas intactas no banco para fins de histórico e auditoria, servindo como a origem de dados para a carga do modelo final.

## Modelagem Relacional (Tabelas Finais)

Para eliminar a redundância e garantir a integridade referencial, o banco foi estruturado seguindo um modelo dimensional/relacional composto por 5 tabelas principais:

1. **`regioes`**: Armazena as grandes regiões do Brasil (`id_regiao`, `sigla_regiao`, `nome_regiao`).
2. **`estados`**: Armazena as Unidades Federativas, vinculadas a uma região através de chave estrangeira (`id_uf`, `nome_uf`, `sigla_uf`, `id_regiao`).
3. **`municipios`**: Armazena os dados dos municípios, vinculados a um estado (`id_municipio`, `nome_municipio`, `id_uf`).
4. **`indicadores`**: Tabela de suporte para cadastrar os tipos de dados analisados de forma dinâmica (ex: 'População Residente').
5. **`fato_indicador_municipal`**: Tabela fato que centraliza as métricas numéricas, associando os IDs de municípios e indicadores aos seus respectivos anos e valores populacionais.

## Lógica das Consultas Desenvolvidas

As consultas foram divididas em dois arquivos:

### 1. queries.sql (Exploração e Validação)
Focado em extrair listas diretas e realizar agregações simples por território. A lógica principal envolve o uso de **`JOINs` sequenciais** (partindo de municípios até regiões) e funções de agregação como **`COUNT()`** e **`SUM()`** combinadas com a cláusula **`GROUP BY`** para totalizar dados de municípios e população por estado e região. Também inclui testes de manipulação de dados (`INSERT`, `UPDATE`, `DELETE`) em ambiente controlado.

### 2. analytics.sql (Visão Analítica)
Consultas avançadas para geração de insights e relatórios gerenciais. A lógica empregada foca em:
- **Rankings e Agrupamentos complexos**: Identificação de assimetrias populacionais utilizando ordenações (`ORDER BY DESC`).
- **Cálculo de Médias**: Uso de funções estatísticas como **`AVG()`** para entender o tamanho médio das cidades por estado.
- **Classificação de Dados**: Aplicação de estruturas condicionais (**`CASE WHEN`** / **`IF`**) para categorizar os municípios dinamicamente em blocos de porte (Pequeno, Médio e Grande) e mensurar a distribuição deles ao longo do território nacional.