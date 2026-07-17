# Entrega Banco de Dados 1 - Leticia Pessoa

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado.

## Arquivos da entrega

- `database.db`: banco SQLite com dados brutos e tabelas criadas.
- `carga.sql`: criação e população das tabelas normalizadas.
- `queries.sql`: consultas SQL obrigatórias.
- `analytics.sql`: consultas analíticas ou proposta de camada analítica.
- `modelo_logico.png`: imagem do modelo lógico feito no DBeaver.

## Dados brutos

As tabelas com prefixo `raw_` foram carregadas automaticamente a partir dos CSVs gerados com dados reais do IBGE.

## Decisões de Modelagem e Normalização

1. **`regioes`**: Isola os dados macro (Norte, Sul, etc) assim como suas respectivas siglas. Como uma região não depende de nenhuma outra tabela, ela é a "raiz" da hierarquia e não possui chave estrangeira.

2. **`estados`**: Possui uma chave estrangeira (`id_regiao`) conectando-se à sua respectiva região. Isolar estado de região evita repetir o nome da região em cada linha, e permite trocar o nome/sigla de uma região em um único lugar sem afetar todos os estados.

3. **`municipio`**: Entidade final da localidade, conectada aos estados via `id_uf`. Assim como estados, evita duplicar `sigla_uf`/`nome_uf` em cada município.

4. **`populacao`**: Tabela associativa que guarda o histórico demográfico de acordo com o ano. Foi definida uma **chave primária composta** (`id_municipio`,`ano`), garantindo que um mesmo munícipio não tenha duas contagens conflitantes no mesmo ano. Embora o arquivo `raw` só possua registros de um ano, essa estrutura já permite inclusão de outros anos no futuro sem alterar o schema.

O arquivo `queries.sql` cobre as duas exigências do enunciado: consultas de leitura com `SELECT`/`JOIN`/`GROUP BY`, e o ciclo completo de `INSERT`/`UPDATE`/`DELETE`.
 
### Consultas de agregação (SELECT, JOIN, GROUP BY)
 
As três primeiras consultas partem diretamente das tabelas normalizadas (e não da view analítica, que só é criada em `analytics.sql`):
 
1. **População total por estado** — encadeia `estados → municipios → populacao` e agrupa por `id_uf`, mostrando quanta gente vive em cada UF.
2. **População total por região** — estende o encadeamento até `regioes`, um nível acima do estado, respondendo à mesma pergunta em uma granularidade maior.
3. **Média populacional dos municípios por estado** — usa `AVG()` sobre o mesmo agrupamento, mostrando o "tamanho típico" de município em cada estado (útil para perceber, por exemplo, que um estado pode ter população total alta mas municípios pequenos, se a população estiver concentrada em poucas cidades).
 
### CRUD
 
O `INSERT`/`UPDATE`/`DELETE` usam o mesmo registro (população de 2026 do Rio de Janeiro) para demonstrar o ciclo de vida completo de um dado na tabela `populacao`, aproveitando a chave primária composta (`id_municipio`, `ano`) para garantir que a operação afete exatamente uma linha, sem risco de alterar registros de outros anos ou municípios.


## Decisões da Camada Analítica (`analytics.sql`)
 
### 1. View de resumo demográfico (`vw_resumo_demografico`)
 
Uma view "larga", que já resolve todos os `JOIN`s entre `regioes`, `estados`, `municipios` e `populacao`. Sem a view, qualquer análise nova precisaria repetir os mesmos três `JOIN`s. Com ela, qualquer consulta futura vira um simples `SELECT ... FROM vw_resumo_demografico WHERE ...`, reduzindo repetição de código e risco de erro.
 
### 2. Ranking dos 10 municípios mais populosos
 
Usa `ORDER BY ... LIMIT 10`, a estrutura mais direta para "top N" quando não é necessário saber a posição exata de cada item, só o conjunto dos maiores.
 
### 3. Top 3 municípios por estado
 
Usa uma função de janela (`RANK() OVER (PARTITION BY sigla_uf ORDER BY valor_populacao DESC)`). A escolha de `RANK()` (em vez de `ROW_NUMBER()`) foi pensada para caso dois municípios empatem em população, ambos devem aparecer com a mesma posição, em vez de um "furar a fila" do outro artificialmente. O uso de `PARTITION BY` é o que garante que a contagem reinicie em cada estado, permitindo comparar municípios apenas dentro do seu próprio contexto estadual.
 
### 4. Concentração populacional (curva acumulada)
 
Usa `SUM() OVER (ORDER BY valor_populacao DESC)` para calcular quanto da população nacional está concentrada nos municípios mais populosos, em ordem decrescente. Essa análise foi incluída porque evidencia visualmente a desigualdade na distribuição populacional brasileira, algo que uma média simples não revela.
 
### 5. Estados acima de um limiar populacional
 
Usa `GROUP BY` + `HAVING`, para filtrar grupos *depois* da agregação (diferente do `WHERE`, que filtraria linhas antes de agrupar). Foi incluída para demonstrar a diferença entre filtrar dados brutos e filtrar resultados agregados.

## Como reproduzir
 
```bash
sqlite3 database.db < schema.sql
sqlite3 database.db < carga.sql
sqlite3 database.db < queries.sql
sqlite3 database.db < analytics.sql
```
 
Os scripts são reexecutáveis: `schema.sql` usa `DROP TABLE IF EXISTS` antes de criar cada tabela, e `analytics.sql` usa `DROP VIEW IF EXISTS` antes de criar a view, então rodar tudo novamente não gera erro de "tabela/view já existe".
