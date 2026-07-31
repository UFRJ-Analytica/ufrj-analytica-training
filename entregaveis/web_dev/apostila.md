# Do zero ao CRUD: FastAPI + uvicorn + Swagger + banco de dados

Este passo a passo mostra a evolução completa: do "Hello World" até uma
API organizada com banco de dados, usando como exemplo os municípios
brasileiros do `database.db` (o mesmo banco que vocês vão usar no
desafio final, descrito em `tarefa.md`). No desafio final, o banco fica
na raiz do repositório `ufrj-analytica-training` e a API fica em
`backend/`.

## Passo 1: Ambiente virtual

Isola as dependências deste projeto do resto do seu computador.

```bash
python3 -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

## Passo 2: Instalar FastAPI e uvicorn

```bash
pip install fastapi "uvicorn[standard]"
```

- **FastAPI**: o framework que define as rotas, valida dados e gera a
  documentação.
- **uvicorn**: o servidor ASGI que efetivamente "escuta" a porta de
  rede e chama o código do FastAPI a cada requisição. O FastAPI
  sozinho não sabe abrir uma porta, quem faz isso é o uvicorn.

## Passo 3: Hello World

Antes de qualquer organização, o menor exemplo possível (`main.py` na
raiz do projeto):

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return {"mensagem": "Hello, World!"}
```

Rodando:

```bash
uvicorn main:app --reload
```

- `main:app` → no arquivo `main.py`, existe uma variável `app`.
- `--reload` → reinicia sozinho a cada alteração de código (só em dev).

Acessando `http://127.0.0.1:8000/` você já vê o JSON `{"mensagem": "Hello, World!"}`.
E sem fazer **nada** a mais, `http://127.0.0.1:8000/docs` já mostra o
Swagger UI, gerado automaticamente pelo FastAPI a partir do próprio
código.

## Passo 4: `.gitignore` e `requirements.txt`

Feito logo no início, antes do projeto crescer:

```
venv/
__pycache__/
*.db
.env
```

- `venv/` nunca vai pro git, cada pessoa cria a sua.
- `__pycache__/` é cache do Python, sem valor pra versionar.
- `*.db` cobre bancos gerados localmente durante o desenvolvimento. O
  `database.db` com os dados do IBGE é diferente: ele já vem pronto e é
  compartilhado com o time, então cabe a vocês decidir se ele entra ou
  não no controle de versão.
- `.env` é onde ficariam segredos (senha de banco, chaves de API).

`requirements.txt` guarda as versões exatas usadas, pra qualquer pessoa
(ou você, em outra máquina) reproduzir o ambiente com
`pip install -r requirements.txt`.

## Passo 5: Organizando em pastas

Um `main.py` sozinho não escala. Antes de adicionar banco de dados,
já separamos por responsabilidade:

```
app/
├── __init__.py
├── main.py          # junta tudo e sobe a aplicação
├── database.py       # conexão com o banco
├── models.py          # tabelas (SQLAlchemy)
├── schemas.py         # formatos de entrada/saída (Pydantic)
├── crud.py            # funções que conversam com o banco
└── routers/
    ├── __init__.py
    └── municipios.py    # endpoints de /municipios
```

| Camada          | Responsabilidade                                 |
|-----------------|---------------------------------------------------|
| `models.py`     | Como o dado é guardado no banco                   |
| `schemas.py`    | Como o dado entra/sai pela API (validação)        |
| `crud.py`       | Lógica de acesso ao banco, sem saber nada de HTTP  |
| `routers/*.py`  | Rotas HTTP: URL, método, status code              |
| `main.py`       | Junta tudo e sobe a aplicação                     |

## Passo 6: Banco de dados (`app/database.py`)

Usamos **SQLite**, apontando direto para o `database.db` que vocês já
têm em mãos (não precisa criar nada, os dados do IBGE já estão lá).
Na estrutura da tarefa, o backend roda a partir de `backend/` e o banco
fica um nível acima, na raiz do repositório.
Trocar para PostgreSQL depois é mudar só a `SQLALCHEMY_DATABASE_URL`,
o resto do código não muda, porque fala com o banco via SQLAlchemy.

## Passo 7: Modelo da tabela (`app/models.py`)

A classe `Municipio` representa a tabela `municipios`: id_municipio,
nome_municipio e id_uf, ligando cada município ao estado dele.

## Passo 8: Schemas de validação (`app/schemas.py`)

Definem o formato de entrada (`MunicipioCreate`, `MunicipioUpdate`) e
saída (`MunicipioResponse`) da API. O FastAPI valida automaticamente
contra esses schemas: se faltar um campo obrigatório ou o `id_uf` não
for um número válido, ele já recusa a requisição antes de chegar no
seu código.

## Passo 9: CRUD (`app/crud.py`)

Funções puras de banco: criar, buscar, listar, atualizar, deletar.
Não sabem nada sobre HTTP.

## Passo 10: Endpoints (`app/routers/municipios.py`)

| Método | Rota                | O que faz                                  |
|--------|---------------------|----------------------------------------------|
| POST   | `/municipios/`      | Cadastra um novo município                  |
| GET    | `/municipios/`      | Lista municípios (paginação via `skip`/`limit`) |
| GET    | `/municipios/{id}`  | Busca um município específico               |
| PUT    | `/municipios/{id}`  | Atualiza um ou mais campos                  |
| DELETE | `/municipios/{id}`  | Remove um município                         |

## Passo 11: Juntando tudo (`app/main.py`)

Cria as tabelas (`Base.metadata.create_all`), instancia o `FastAPI` com
título/descrição (que aparecem no Swagger), e inclui o router de
municípios com `app.include_router(municipios.router)`.

## Rodando o projeto final

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Depois acesse:
- **http://127.0.0.1:8000/docs**: Swagger UI, testa tudo clicando.
- **http://127.0.0.1:8000/redoc**: documentação alternativa, focada em leitura.

## Exemplo via curl

```bash
curl -X POST http://127.0.0.1:8000/municipios/ \
  -H "Content-Type: application/json" \
  -d '{"nome_municipio": "Nova Esperança", "id_uf": 33}'

curl http://127.0.0.1:8000/municipios/
curl -X PUT http://127.0.0.1:8000/municipios/1 -H "Content-Type: application/json" -d '{"nome_municipio": "Nova Esperança do Sul"}'
curl -X DELETE http://127.0.0.1:8000/municipios/1
```

(`id_uf: 33` é o Rio de Janeiro, conferido direto na tabela `estados` do `database.db`.)

## Próximos passos sugeridos

- Autenticação (só um gestor autorizado pode criar/editar/remover registros).
- Migrações com **Alembic**, em vez de `create_all`.
- Testes automatizados com `pytest` + `TestClient` do FastAPI.

Quando terminar de entender esses passos, o desafio de verdade está em `tarefa.md`.
