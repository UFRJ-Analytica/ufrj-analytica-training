# Padrao de Commits | Analytica

Este documento define um padrao simples para nomes de commits no projeto.

## Formato

```text
TIPO/ descricao-curta-em-minusculo
```

Exemplos:

```text
feat/ cria-pagina-de-equipe
chore/ adiciona-requirements
WIP/ estrutura-inicial-do-app
FIX/ corrige-leitura-do-csv
```

## Tipos de commit

### `feat/`
Usar quando houver nova funcionalidade.

Exemplos:
- `feat/ adiciona-filtro-de-projetos`
- `feat/ cria-dashboard-inicial`

### `chore/`
Usar para tarefas de manutencao, organizacao ou infraestrutura que nao alteram diretamente uma funcionalidade.

Exemplos:
- `chore/ atualiza-dependencias`
- `chore/ reorganiza-estrutura-de-pastas`

### `WIP/`
Usar apenas para trabalho em andamento, quando a entrega ainda nao esta finalizada.

Regras:
- Evitar manter `WIP/` na branch principal.
- Substituir por commit final mais claro antes de mergear, quando possivel.

Exemplos:
- `WIP/ monta-base-da-home`
- `WIP/ inicia-pagina-de-projetos`

### `FIX/`
Usar para correcao de bug, erro de regra ou comportamento quebrado.

Exemplos:
- `FIX/ corrige-filtro-da-equipe`
- `FIX/ ajusta-caminho-do-arquivo-csv`

## Tipos adicionais recomendados

### `docs/`
Usar para documentacao.

Exemplos:
- `docs/ adiciona-guia-de-execucao`
- `docs/ atualiza-padrao-de-commits`

### `refactor/`
Usar para melhoria interna de codigo sem mudar comportamento esperado.

Exemplos:
- `refactor/ simplifica-carregamento-de-dados`
- `refactor/ separa-funcoes-de-utilidade`

### `test/`
Usar para criacao ou ajuste de testes.

Exemplos:
- `test/ adiciona-cobertura-para-filtros`
- `test/ ajusta-casos-de-validacao`

### `style/`
Usar para ajustes visuais ou de formatacao sem impacto funcional relevante.

Exemplos:
- `style/ melhora-layout-da-home`
- `style/ padroniza-espacamento-das-paginas`

## Regras gerais

- Escrever a descricao em minusculo.
- Preferir frases curtas e objetivas.
- Usar verbo no inicio da descricao.
- Evitar commits vagos como `feat/ mudancas` ou `FIX/ ajuste`.
- Um commit deve representar uma mudanca clara.
