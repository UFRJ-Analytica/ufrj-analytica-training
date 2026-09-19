# Capacitação DevOps — Docker

## Entregáveis 1 e 2

Nesta atividade, vocês irão containerizar o projeto utilizado nas capacitações da UFRJ Analytica.

O objetivo é que, ao final, o **frontend**, o **backend** e os serviços necessários da aplicação possam ser executados utilizando Docker e Docker Compose.

> **Importante:** GitHub Actions, CI/CD e deploy automático serão abordados em uma segunda capacitação. Nesta entrega, o foco é exclusivamente Docker, Dockerfiles e Docker Compose.

---

# Estrutura do projeto

O repositório está organizado a partir da raiz:

```text
ufrj-analytica-training/
│
├── backend/
├── frontend/
├── entregaveis/
│   └── devops_docker_1/
└── ...
```

Durante o desenvolvimento da atividade, os arquivos Docker devem ser criados nas posições corretas do projeto para que seja possível testar a aplicação.

Estrutura esperada:

```text
ufrj-analytica-training/
│
├── Dockerfile
├── compose.yaml
│
├── backend/
│   ├── Dockerfile
│   └── ...
│
├── frontend/
│   └── ...
│
└── entregaveis/
    └── devops_docker_1/
```

> O `Dockerfile` localizado na raiz será responsável pelo frontend.  
> O `backend/Dockerfile` será responsável pela API.

---

# Entregável 1 — Containerização da aplicação

O primeiro entregável consiste em criar as imagens Docker do **frontend** e do **backend**.

## 1. Dockerfile do Frontend

Criem:

```text
ufrj-analytica-training/Dockerfile
```

Esse Dockerfile deve:

- utilizar uma imagem base adequada;
- definir o diretório de trabalho;
- instalar as dependências do frontend;
- copiar os arquivos necessários;
- expor a porta utilizada pela aplicação;
- iniciar corretamente o frontend.

O container do frontend deve conseguir ser executado de forma independente.

Exemplo do fluxo esperado:

```bash
docker build -t analytica-frontend .
docker run -p <porta-host>:<porta-container> analytica-frontend
```

---

## 2. Dockerfile do Backend

Criem:

```text
ufrj-analytica-training/backend/Dockerfile
```

Esse Dockerfile deve:

- utilizar uma imagem Python adequada;
- definir o diretório de trabalho;
- instalar as dependências do backend;
- copiar os arquivos da API;
- expor a porta da aplicação;
- executar o FastAPI com Uvicorn.

A API atualmente pode ser executada localmente com:

```bash
uvicorn app.main:app --reload
```

Dentro do container, o servidor deve aceitar conexões externas ao próprio container.

Após subir a API, a documentação deverá estar acessível em:

```text
http://localhost:8000/docs
```

ou na porta que vocês definirem no host.

---

## 3. Testar os dois containers

Antes de continuar para o Docker Compose, verifiquem se os dois Dockerfiles conseguem gerar suas respectivas imagens.

Comandos úteis:

```bash
docker build
docker run
docker ps
docker logs
```

Os containers devem iniciar sem erros que impeçam o funcionamento das aplicações.

---

# Entregável 2 — Orquestração com Docker Compose

Depois de validar os Dockerfiles individualmente, criem um arquivo Docker Compose na raiz do projeto:

```text
ufrj-analytica-training/compose.yaml
```

ou:

```text
ufrj-analytica-training/docker-compose.yml
```

Utilizem apenas um dos formatos.

O Compose deve integrar, no mínimo:

```text
frontend
backend
```

Caso o projeto utilize um banco de dados executado como serviço separado, ele também deverá fazer parte do Compose.

Exemplo conceitual:

```text
Docker Compose
     │
     ├── frontend
     ├── backend
     └── database
```

---

## Requisitos do Compose

### Services

Cada parte da aplicação deve ser declarada como um serviço.

Exemplo:

```yaml
services:
  frontend:
    # ...

  backend:
    # ...
```

### Build

O Compose deve utilizar os Dockerfiles criados no Entregável 1.

Ele deverá saber onde encontrar:

```text
./Dockerfile
./backend/Dockerfile
```

### Portas

As portas necessárias devem ser publicadas para que a aplicação possa ser acessada pelo computador do usuário.

Exemplo conceitual:

```text
HOST : CONTAINER
3000 : 3000
8000 : 8000
```

Utilizem as portas reais do projeto.

### Network

Frontend e backend devem conseguir se comunicar pela rede do Docker Compose.

Dentro de uma rede Docker, normalmente utilizamos o **nome do serviço** para acessar outro container.

Exemplo:

```text
http://backend:8000
```

e não:

```text
http://localhost:8000
```

quando a comunicação estiver acontecendo **de um container para outro**.

### Volumes

Caso algum serviço necessite persistir dados, configurem um volume.

O objetivo é evitar que informações importantes sejam perdidas apenas porque um container foi removido.

Exemplo conceitual:

```yaml
volumes:
  dados:
```

### Variáveis de ambiente

Caso a aplicação utilize configurações por ambiente, elas podem ser declaradas no Compose ou carregadas por arquivo `.env`.

Não adicionem senhas, tokens ou credenciais reais ao repositório.

Quando necessário, utilizem:

```text
.env.example
```

### Healthcheck

Quando fizer sentido para a arquitetura utilizada, adicionem um `healthcheck` para validar se um serviço está realmente pronto para receber requisições.

É importante compreender a diferença entre:

```text
container iniciado
```

e:

```text
aplicação pronta
```

Se houver dependência entre serviços, vocês também podem utilizar `depends_on`.

---

# Teste final

A aplicação deve poder ser iniciada a partir da raiz do projeto utilizando:

```bash
docker compose up --build
```

Após o comando, verifiquem:

- frontend funcionando;
- backend funcionando;
- comunicação entre os serviços;
- banco funcionando, caso utilizado;
- ausência de erros críticos nos logs.

Comandos úteis:

```bash
docker compose ps
docker compose logs
docker compose logs backend
docker compose logs frontend
docker ps
```

Para encerrar:

```bash
docker compose down
```

---

# Como entregar

Depois de concluir e testar a atividade, cada trainee deverá criar uma pasta com o próprio nome e sobrenome dentro de:

```text
ufrj-analytica-training/entregaveis/devops_docker_1/
```

Utilizem o padrão:

```text
nome-sobrenome
```

Exemplo:

```text
entregaveis/
└── devops_docker_1/
    └── gustavo-costa/
```

Depois que tudo estiver funcionando, **copiem ou movam para a pasta da entrega os arquivos Docker criados por vocês**.

A entrega deverá possuir uma estrutura semelhante a:

```text
entregaveis/
└── devops_docker_1/
    └── nome-sobrenome/
        ├── Dockerfile
        ├── backend.Dockerfile
        ├── compose.yaml
        └── evidencia.png
```

Como existem dois arquivos chamados `Dockerfile` durante o desenvolvimento, renomeiem o Dockerfile do backend **apenas dentro da pasta da entrega**, por exemplo:

```text
backend.Dockerfile
```

Não é necessário alterar o nome do arquivo original dentro de `backend/`.

Arquivos adicionais relevantes também podem ser incluídos, por exemplo:

```text
.dockerignore
.env.example
```

---

# Evidência obrigatória

A entrega deve conter pelo menos **uma evidência de que os containers estão funcionando**.

Pode ser:

- print do Docker Desktop mostrando os containers ativos;
- print do terminal executando `docker compose ps`;
- print dos logs dos containers;
- print da aplicação funcionando junto aos containers;
- outra evidência equivalente que demonstre claramente a execução.

Exemplos de nomes:

```text
evidencia.png
containers.png
docker-desktop.png
logs.png
```

Vocês podem enviar mais de uma imagem.

---

# Critérios de conclusão

## Entregável 1

- [ ] Criou o Dockerfile do frontend.
- [ ] Criou o Dockerfile do backend.
- [ ] Conseguiu gerar as duas imagens.
- [ ] Conseguiu iniciar os containers.
- [ ] Frontend e backend funcionam dentro dos containers.

## Entregável 2

- [ ] Criou o arquivo Docker Compose.
- [ ] Frontend e backend estão definidos como serviços.
- [ ] Os Dockerfiles corretos são utilizados no build.
- [ ] As portas necessárias foram configuradas.
- [ ] Os containers conseguem se comunicar quando necessário.
- [ ] Volumes foram utilizados quando houver necessidade de persistência.
- [ ] O projeto sobe com `docker compose up --build`.
- [ ] Existe evidência visual dos containers funcionando.

---

# Resultado esperado

Ao final da atividade, alguém que possui Docker instalado deverá conseguir chegar à raiz do projeto e executar:

```bash
docker compose up --build
```

e ter o ambiente necessário da aplicação funcionando sem precisar configurar manualmente cada serviço.

Esse é um dos principais objetivos da containerização:

> **transformar o ambiente da aplicação em uma configuração reproduzível.**

---

# Próxima etapa

GitHub Actions, testes automáticos, CI/CD e deploy automático **não fazem parte desta entrega**.

Esses assuntos serão trabalhados na próxima etapa da capacitação de DevOps.
