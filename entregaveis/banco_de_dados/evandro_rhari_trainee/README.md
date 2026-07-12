# Entrega Banco de Dados 1 - Evandro Rhari

## Objetivo

Transformar as tabelas brutas `raw_` em um modelo relacional normalizado.

## Arquivos da entrega

- `database.db`: banco SQLite com dados brutos e tabelas criadas.
- `normalizacao.sql`: criação e população das tabelas normalizadas.
- `queries.sql`: consultas SQL obrigatórias.
- `analytics.sql`: consultas analíticas ou proposta de camada analítica.
- `modelo_logico.png`: imagem do modelo lógico feito no DBeaver.

## Dados brutos

As tabelas com prefixo `raw_` foram carregadas automaticamente a partir dos CSVs gerados com dados reais do IBGE.

A partir delas, crie o modelo final normalizado.

## Normalização

Os dados foram normalizados até a terceira forma normal.
Os dados são todos atômicos a medida do prático. Argumentavelmente, `populacao_municipal.fonte` não está atômico, pois referência uma tabela em uma base (que são duas informações), mas, considerando que todas as entradas tem a mesma origem, não considerei necessária a separação nesse estágio do desenvolvimento, focando em polir outras partes do desenvolvimento dado meu tempo limitado para trabalhar na entrega. Mesma as informações sendo as mesmas (inclusive em outros campos), eu os mantive, pois não sei o objetivo do criador dessa tabela e não me sinto confortável apagando sem ter certeza.

## Lógica das queries

A lógica das consultas foi descrita em comentários através do dos arquivos, mas, de maneira geral, busquei fazer um código intuitivo, com aliases e identações que buscam explicitar o funcionamento do código.

Os códigos foram rodados no VSCode usando sqlite3 no terminal e a extensão SQLite Viewer do FLorian Klampfer. No entanto, elas também foram estadas do Dbeaver. O sistema operacional usado foi um derivado de Arch Linux.

O arquivo `normalização.sh` foi criado para criar e popular as tabelas no normalizadas com apenas um comando no terminal.