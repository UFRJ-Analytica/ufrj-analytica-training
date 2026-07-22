# Tarefa de WebDev (tá facinho 😅): sistema de acompanhamento populacional

<img style="width: 120px" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZAuU4oeu14WhiqdZFl9T78EQwIwgwMUyYGm_BoXrTkA&s=10" />

Se vocês ainda não passaram pelo `apostila.md`, comecem por lá: ele cobre o básico de FastAPI com um exemplo pequeno, o CRUD de municípios. Aqui é a vez de vocês aplicarem isso sozinhos, num cenário maior, com o desafio completo (análise e cadastro).

## O que vocês vão construir

Um sistema pequeno para gestores acompanharem dados de população dos municípios brasileiros. Pensem nele como uma ferramenta de apoio à decisão: de um lado, telas de análise que ajudam a entender como a população está distribuída entre regiões, estados e municípios. Do outro, uma parte de cadastro, onde o gestor registra e atualiza informações próprias sobre cada município, do tipo que não vem em nenhum dado do IBGE.

Por exemplo: o gestor pode olhar o painel, perceber que um município pequeno está com população crescendo rápido, e querer marcar esse município como "prioridade de acompanhamento", com uma observação explicando o motivo. Isso é cadastro. Depois ele pode voltar e editar essa observação, ou remover. O sistema de vocês precisa suportar esse ciclo completo.

Essas informações de cadastro não existem no banco que vocês vão receber. Isso é proposital. Parte do exercício é vocês decidirem que campos fazem sentido guardar e criar essa estrutura no banco.

O sistema tem duas partes: uma API em FastAPI e uma tela em Streamlit que consome essa API. A API fica na pasta `backend/`, dentro do repositório de treinamento, e a tela em Streamlit fica na aplicação principal do próprio repositório. O que preparamos é a estrutura de projeto, o banco de dados e um exemplo de endpoint funcionando, só para mostrar o padrão a seguir.

## O que vocês vão receber

A partir da raiz do repositório `ufrj-analytica-training`, a estrutura relevante é:

```
database.db              banco SQLite com dados do IBGE
backend/                  projeto do backend em FastAPI
├── requirements.txt
├── .gitignore
└── app/
    ├── main.py            endpoints da API
    ├── database.py        conexão com o SQLite, já pronta
    ├── schemas.py         modelos Pydantic
    └── endpoints/         endpoints separados por trainee
app.py                    aplicação principal em Streamlit
pages/                    páginas da aplicação Streamlit
requirements.txt          dependências do Streamlit
```

Usem um ambiente virtual para instalar as dependências. O `.gitignore` do repositório já exclui `.venv/` e `venv/`, então o ambiente local não deve ser versionado.

## O banco de dados

O `database.db` tem dados populacionais do IBGE, estimativa de 2025, em quatro tabelas:

| Tabela | Conteúdo |
|---|---|
| `regioes` | as 5 regiões do Brasil |
| `estados` | os 27 estados, cada um ligado a uma região |
| `municipios` | os 5.570 municípios, cada um ligado a um estado |
| `populacao_municipal` | a população de cada município em 2025 |

Antes de escrever qualquer código, abram o banco (com `sqlite3 database.db` no terminal, ou a extensão de SQLite do editor de vocês) e explorem as tabelas. Entender os dados é o primeiro passo.

## Parte 1: a API em FastAPI

O endpoint `GET /regioes`, em `backend/app/main.py`, já está pronto, olhem para ele como referência de padrão: recebe parâmetros, monta uma query, valida a resposta com Pydantic, devolve JSON.

Como várias pessoas vão trabalhar no mesmo repositório, não concentrem tudo no `main.py`. Cada trainee deve criar seus endpoints em um arquivo próprio dentro de `backend/app/endpoints/`, seguindo o padrão `backend/app/endpoints/nome_sobrenome.py` (por exemplo, `backend/app/endpoints/ana_silva.py`). Dentro desse arquivo, criem um `router` do FastAPI e implementem as rotas da parte que vocês forem desenvolver.

Exemplo de estrutura mínima:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/ana-silva", tags=["ana_silva"])


@router.get("/status")
def status():
    return {"status": "ok"}
```

O `backend/app/main.py` já importa automaticamente os arquivos que tiverem um `router` dentro de `backend/app/endpoints/`. Se vocês preferirem fazer o registro manual, importem o arquivo no `main.py` e chamem `app.include_router(nome_sobrenome.router)`. Em qualquer caso, não editem o arquivo de endpoint de outra pessoa.

A API precisa cobrir duas frentes:

**Consulta e análise.** Endpoints que alimentam os gráficos do painel. A lista abaixo cobre os tipos de informação que o painel precisa ter, cada um pedindo um tipo diferente de consulta no banco:

- Números resumo (KPIs): total de municípios, total de estados, população total do Brasil, ano de referência dos dados, e qual é o município mais populoso.
- Top N municípios mais populosos: uma lista ordenada, tipo "top 5" ou "top 10" (deixem a quantidade configurável), pra virar tanto uma tabela quanto um gráfico de barras.
- População total por região: pra um gráfico de pizza ou donut mostrando a fatia de cada região no país.
- População total por estado, com filtro opcional por região: pra um gráfico de barras comparando estados.
- Distribuição da população de todos os municípios: pra um histograma (a maioria dos municípios brasileiros é pequena, poucos são enormes, isso deve aparecer no gráfico).
- Quantidade de municípios x população média por estado: pra um gráfico de dispersão, colorido por região.
- Mapa de calor cruzando região com porte do município: classifiquem cada município em pequeno, médio ou grande (definam os limites de população que fizerem sentido) e contem quantos municípios de cada porte existem em cada região. O resultado é uma matriz região x porte, que vira um heatmap colorido pela quantidade.

Façam a agregação no banco, não devolvam a tabela crua para o Streamlit processar.

**Município (dados básicos).** Além de listar e buscar, a API precisa deixar o gestor cadastrar um município novo e atualizar os dados de um existente: nome, estado e população. Como um município novo não tem um código oficial do IBGE, gerem um id vocês mesmos (por exemplo, o maior id_municipio já usado, mais 1). Pensem em REST: POST para criar, PUT ou PATCH para atualizar, DELETE para remover.

**Cadastro.** Endpoints para criar, listar, editar e remover as informações que o gestor registra sobre um município (diferente do item acima: aqui é uma anotação do gestor, não um dado do IBGE). Vocês decidem os campos (status, prioridade, observação, responsável, o que fizer sentido), criam a tabela no SQLite para guardar isso, e implementam as rotas correspondentes. Pensem em REST: um POST para criar, GET para listar, PUT ou PATCH para editar, DELETE para remover.

Usem `response_model` do Pydantic sempre que fizer sentido, para que o Swagger documente o formato da resposta sozinho. Tratem erros como município inexistente com o status HTTP correto. Testem cada endpoint pela documentação automática em `http://127.0.0.1:8000/docs` antes de conectar no Streamlit.

## Parte 2: a tela em Streamlit

Arquivos `app.py` e `pages/`, na raiz do repositório. Usem a aplicação Streamlit existente como base para criar as telas do sistema e consumir a API com `requests`.

Para evitar sobrescrever o trabalho de outra pessoa, cada trainee deve criar sua própria tela no padrão `pages/nome_sobrenome.py` (por exemplo, `pages/ana_silva.py`). Não coloquem a tela principal da tarefa no `app.py` nem editem a página de outro trainee.

O sistema final precisa ter uma área de análise com todos os tipos de informação listados na Parte 1: os KPIs no topo, a lista/gráfico de top N municípios, a pizza por região, as barras por estado, o histograma de distribuição, o scatter de municípios x população média, e o heatmap de região x porte. Acrescentem filtros interativos como seletor de região ou estado onde fizer sentido.

Precisa também de uma área de cadastro, com duas partes: uma pra criar um município novo ou editar nome/estado/população de um existente, e outra pra ver as informações que o gestor registrou sobre um município (a anotação do item "Cadastro" da Parte 1), adicionar uma nova, editar ou remover.

Não acessem o banco direto pelo Streamlit. Toda comunicação passa pela API, via `requests`. Se a API estiver fora do ar, mostrem uma mensagem em vez de deixar a tela quebrar.

## Como rodar

Terminal 1, a API:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Documentação em `http://127.0.0.1:8000/docs`.

Terminal 2, a tela:

```bash
cd ufrj-analytica-training
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O endereço aparece no terminal, geralmente `http://localhost:8501`.

Se o ambiente virtual já existir, basta ativá-lo e instalar/atualizar as dependências com `pip install -r requirements.txt`.

## Critérios de avaliação

| Tarefa | API | Tela |
|---|---|---|
| KPIs (resumo) | Responde com os números certos: total de municípios, total de estados, população total, ano de referência e município mais populoso | Os números aparecem em destaque no topo do painel |
| Top N municípios mais populosos | Responde com a lista ordenada, respeitando a quantidade pedida | Aparece como tabela e como gráfico de barras, com controle pra mudar a quantidade |
| População por região | Responde com o total agregado por região | Aparece como gráfico de pizza ou donut |
| População por estado | Responde com o total por estado e filtra por região quando pedido | Aparece como gráfico de barras, com o filtro de região funcionando |
| Distribuição da população | Responde com os valores de população de todos os municípios | Aparece como histograma |
| Dispersão município x estado | Responde com quantidade de municípios e população média por estado | Aparece como gráfico de dispersão, colorido por região |
| Mapa de calor região x porte | Responde com a contagem de municípios cruzando região e porte | Aparece como mapa de calor |
| Município (criar, atualizar, remover) | Cada rota faz o CRUD de verdade no banco: criar grava um município novo (com id gerado), atualizar muda nome/estado/população, remover apaga | A tela permite cadastrar um município novo e editar/remover um existente, e as mudanças continuam lá depois de atualizar a página |
| Cadastro (criar, listar, editar, remover) | Cada rota faz o CRUD de verdade no banco: criar grava um registro novo, listar traz os certos, editar atualiza, remover apaga | A tela permite fazer as quatro ações num município escolhido, e os dados continuam lá depois de atualizar a página |

Bom trabalho.
