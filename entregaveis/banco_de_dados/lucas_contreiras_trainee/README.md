# Entrega Banco de Dados 1 - Lucas Contreiras

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado, com posterior exploração e análise dos dados de IBGE (regiões, estados, municípios e indicadores de população).

## Arquivos da entrega

- `database.db`: banco SQLite com dados brutos e tabelas normalizadas.
- `schema.sql`: criação das tabelas normalizadas (regiões, estados, municípios, indicadores, fato_indicador_municipal).
- `carga.sql`: população das tabelas normalizadas a partir das tabelas brutas.
- `queries.sql`: 10 consultas SQL obrigatórias para exploração e validação.
- `analytics.sql`: 6 consultas analíticas para análise estratégica de população.
- `modelo_logico.png`: diagrama lógico do modelo relacional da entrega.
- `README.md`: documentação da entrega (este arquivo).

## Dados brutos

As tabelas com prefixo `raw_` foram carregadas automaticamente a partir dos CSVs gerados com dados reais do IBGE:
- `raw_regioes`: dados de regiões (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)
- `raw_estados`: dados de estados/UFs por região
- `raw_municipios`: dados de municípios por estado
- `raw_populacao_municipal`: dados de população estimada para cada município
- `raw_municipios_com_populacao`: dados consolidados (join de raw_municipios + raw_populacao_municipal)
- `metadata_carga`: metadados da carga (data, usuário, quantidade de registros)

## Modelo de dados normalizado

### Estrutura de tabelas

```
regioes
├── id_regiao (PK)
├── sigla_regiao
├── nome_regiao
└── relacionamento 1:N com estados

estados
├── id_uf (PK)
├── id_regiao (FK → regioes)
├── nome_uf
└── sigla_uf

municipios
├── id_municipio (PK)
├── id_uf (FK → estados)
├── nome_municipio
└── relacionamento N:1 com estados

indicadores
├── id_indicador (PK)
├── nome_indicador
└── relacionamento 1:N com fato_indicador_municipal

fato_indicador_municipal
├── id_municipio (PK/FK → municipios)
├── id_indicador (PK/FK → indicadores)
├── ano (PK)
└── valor
```

### Decisões de design

1. **Normalização**: As tabelas foram estruturadas em 3ª forma normal (3NF) para eliminar redundâncias.
2. **Dimensões separadas**: Regiões, Estados e Municípios são tabelas de dimensão independentes.
3. **Tabela Fato**: A tabela `fato_indicador_municipal` centraliza os dados de indicadores, permitindo fácil extensão para novos indicadores.
4. **Chaves primárias e estrangeiras**: Todas as relações foram estabelecidas com constraints de integridade referencial.

## Consultas SQL - Parte 2

### queries.sql (10 consultas obrigatórias)

1. **Q1 - Listar regiões**: Retorna todas as regiões do Brasil.
2. **Q2 - Estados por região**: Mostra estados filtrando por uma região específica (exemplo: Sudeste).
3. **Q3 - Municípios por estado**: Lista municípios de um estado (exemplo: SP).
4. **Q4 - Municipío com estado e região**: JOIN de 3+ tabelas retornando localização geográfica com população.
5. **Q5 - Detalhes de população**: Consulta com JOIN mostrando indicadores de população por município.
6. **Q6 - Contagem por estado**: GROUP BY + COUNT para contar municípios por estado.
7. **Q7 - Contagem por região**: GROUP BY + COUNT para contar municípios por região.
8. **Q8 - Agregação de população**: SUM agregando população por estado.
9. **Q9 - Top 10 estados**: query com `ORDER BY` + `LIMIT` retornando estados com maior quantidade de municípios.
10. **Q10 - Demonstração DML**: CREATE TABLE, INSERT, UPDATE, DELETE em uma tabela de teste.

### analytics.sql (6 consultas analíticas)

1. **A1 - Ranking de municípios**: Top 20 municípios mais populosos com ranking.
2. **A2 - Ranking de estados**: Top 10 estados mais populosos com agregações.
3. **A3 - Distribuição por região**: Análise de concentração populacional por região.
4. **A4 - Classificação de tamanho**: Categoriza municípios em classes de tamanho (Metrópole, Grande, Médio, Pequeno).
5. **A5 - Acima da média**: Identifica municípios com população acima da média do estado.
6. **A6 - Concentração (Pareto)**: Análise da concentração de população (top 20% de municípios concentra quantos % da população).

## Como validar

1. **Abrir no DBeaver**:
   ```
   File > New Database Connection > SQLite
   Set path: entregaveis/banco_de_dados/lucas_contreiras_trainee/database.db
   ```

2. **Executar queries.sql**: Copiar e colar as queries e executar uma por uma.

3. **Executar analytics.sql**: Copiar e colar as queries analíticas e validar análises.

4. **Validar integridade**: Verificar que os dados fazem sentido (ex: total de municípios, soma de população).

## Próximos passos

- Todas as 10 queries obrigatórias foram implementadas em `queries.sql`.
- Todas as 6 queries analíticas foram implementadas em `analytics.sql`.
- Recomenda-se testar em DBeaver antes de submeter a entrega.
