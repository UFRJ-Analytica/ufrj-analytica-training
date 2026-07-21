# Entrega Banco de Dados 1 - Leticia Pessoa

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado e propor uma camada analítica sobre esse modelo.

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

## Consultas obrigatórias (`queries.sql`)
 
O arquivo cobre as duas exigências do enunciado: consultas de leitura com `SELECT`/`JOIN`/`GROUP BY` (1 a 9), e o ciclo completo de `INSERT`/`UPDATE`/`DELETE` (10).
 
### Consultas de leitura (1 a 9)
 
As consultas percorrem a hierarquia geográfica de forma progressiva — primeiro isoladas, depois combinadas — para demonstrar `JOIN`s em diferentes profundidades:
 
1. **Regiões existentes na base** — leitura direta de `regioes`, sem `JOIN`, serve de ponto de partida.
2. **Estados de uma região escolhida** — primeiro `JOIN` da cadeia (`estados` + `regioes`), filtrado por `nome_regiao`.
3. **Municípios de uma UF escolhida** — mesmo padrão, um nível abaixo (`municipios` + `estados`), filtrado por `sigla_uf`.
4. **Estado e região de cada município** — encadeia os dois `JOIN`s anteriores em uma única consulta, sem filtro, mostrando a hierarquia completa por município.
5. **População de cada município (município, UF, região, ano, valor)** — estende a consulta 4 até `populacao`, chegando à granularidade mais fina do modelo.
6. **Quantidade de municípios por estado** — primeira consulta com `GROUP BY` + `COUNT`, respondendo "quantos municípios tem cada UF".
7. **Quantidade de municípios por região** — mesma lógica da 6, um nível de agregação acima.
8. **População total por estado** — troca `COUNT` por `SUM(valor_populacao)`, agregando o histórico demográfico por UF.
9. **Top 10 estados com mais municípios** — reaproveita a consulta 6, ordenando por `qtd_municipios` e aplicando `LIMIT 10`.

### CRUD (10): Create | Read | Update | Delete
 
Em vez de inserir/alterar/remover diretamente na tabela `populacao` (que guarda os dados reais usados nas análises), o CRUD é demonstrado em uma tabela descartável, criada e destruída dentro do próprio script.

## Decisões da Camada Analítica (`analytics.sql`)

 A camada analítica foi pensada como uma **segunda camada, construída em cima do modelo normalizado**, focando em torná-los fáceis de consultar para responder perguntas de pesquisa. Todas as 8 análises partem de `vw_resumo_demografico`, em vez de repetir os `JOIN`s entre `regioes`, `estados`, `municipios` e `populacao` em cada uma. Se a hierarquia geográfica mudar um dia, só a view precisa ser ajustada.
 
### View de resumo demográfico (`vw_resumo_demografico`)
 
Resolve todos os `JOIN`s da hierarquia geográfica e adiciona um filtro: `WHERE pop.ano = (SELECT MAX(ano) FROM populacao)`. Essa cláusula garante que a view sempre reflita o **ano mais recente disponível**, mesmo que a tabela `populacao` seja atualizada no futuro com múltiplos anos.
 
### 1. Top 10 municípios mais populosos
 
`ORDER BY ... LIMIT 10` sobre a view — a forma mais direta de responder "quais os maiores", sem precisar da posição exata de cada um.
 
### 2. Top 3 municípios por UF
 
Função de janela `RANK() OVER (PARTITION BY sigla_uf ORDER BY valor_populacao DESC)`. `RANK()` foi escolhido em vez de `ROW_NUMBER()` para que municípios empatados em população dividam a mesma posição. `PARTITION BY` reinicia a contagem a cada UF, respondendo a uma pergunta que um `GROUP BY` simples não conseguiria, pois colapsaria os municípios em uma única linha por estado.
 
### 3. Concentração populacional (curva acumulada)
 
`SUM() OVER (ORDER BY valor_populacao DESC)` calcula quanto da população nacional está concentrada nos municípios mais populosos. Evidencia a desigualdade na distribuição populacional brasileira, algo que uma média simples não revela.
 
### 4. Estados com população acima de um limiar
 
`GROUP BY` + `HAVING`, filtrando grupos *depois* da agregação (diferente do `WHERE`, que filtraria linhas antes de agrupar) — só é possível saber a população total de um estado depois de somar seus municípios.
 
### 5. População total por região
 
`GROUP BY nome_regiao` + `SUM`, mesma lógica da consulta 4 de `queries.sql`, mas agora a partir da view já filtrada pelo último ano, e em um nível de agregação acima (região em vez de estado).
 
### 6. Média populacional dos municípios por estado
 
`AVG(valor_populacao)` agrupado por estado, mostra o "tamanho típico" de município em cada UF, revelando estados com população total alta mas concentrada em poucas cidades grandes.
 
### 7. Municípios acima da média nacional
 
Usa uma subconsulta (`WHERE valor_populacao > (SELECT AVG(valor_populacao) FROM vw_resumo_demografico)`) para comparar cada município a um valor de referência calculado sobre toda a base, uma forma de identificar outliers sem precisar definir manualmente um limite fixo.
 
### 8. Classificação por porte populacional
 
`CASE WHEN` cria faixas de porte (Pequeno, Médio, Grande, Metrópole) que não existem como coluna na base, e `GROUP BY` sobre essa expressão calculada mostra quantos municípios — e quanta população — cada faixa concentra. Revela, tipicamente, que a maioria dos municípios brasileiros é pequena, mas a maior parte da população vive em poucas cidades grandes.

## Como reproduzir
 
```bash
sqlite3 database.db < schema.sql
sqlite3 database.db < carga.sql
sqlite3 database.db < queries.sql
sqlite3 database.db < analytics.sql
```
 
Os scripts são reexecutáveis: `schema.sql` usa `DROP TABLE IF EXISTS` antes de criar cada tabela, e `analytics.sql` usa `DROP VIEW IF EXISTS` antes de criar a view, então rodar tudo novamente não gera erro de "tabela/view já existe", e o CRUD de `queries.sql` limpa a própria tabela de teste ao final — então rodar tudo novamente não gera erro de "tabela/view já existe" nem deixa dados residuais.
 

