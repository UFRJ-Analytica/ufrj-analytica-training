"""
API do sistema de acompanhamento populacional (IBGE) para gestores.

O endpoint `/regioes` está implementado como exemplo do padrão a seguir:
query -> banco -> validação com Pydantic -> retorno.

O restante são stubs. Veja o tarefa.md para entender o que cada grupo
de endpoints precisa fazer.

Para rodar:
    uvicorn app.main:app --reload

Depois acesse a documentação interativa em http://127.0.0.1:8000/docs
"""
import importlib
import pkgutil

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import endpoints
from database import query
from schemas import Regiao

app = FastAPI(
    title="UFRJ Analytica - Sistema de Acompanhamento Populacional",
    description="API construída durante a capacitação de WebDev para Ciência de Dados.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def incluir_endpoints_dos_trainees() -> None:
    """Importa automaticamente rotas criadas em app/endpoints/*.py."""
    for module_info in pkgutil.iter_modules(endpoints.__path__):
        module = importlib.import_module(f"endpoints.{module_info.name}")

        router = getattr(module, "router", None)
        if router is not None:
            app.include_router(router)
            continue

        trainee_app = getattr(module, "app", None)
        if isinstance(trainee_app, FastAPI):
            for route in trainee_app.router.routes:
                if route.path not in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
                    app.router.routes.append(route)


incluir_endpoints_dos_trainees()


@app.get("/", tags=["status"])
def root():
    return {"status": "ok", "mensagem": "API no ar. Veja /docs para a documentação."}


# ---------------------------------------------------------------------------
# Exemplo pronto, use como referência.
# ---------------------------------------------------------------------------
@app.get("/regioes", response_model=list[Regiao], tags=["dados básicos"])
def listar_regioes():
    rows = query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return rows


# ---------------------------------------------------------------------------
# Consulta e análise: endpoints que alimentam os gráficos do painel.
# ---------------------------------------------------------------------------

@app.get("/estados", tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    """TODO: listar estados, com filtro opcional por região."""
    raise HTTPException(status_code=501, detail="TODO: implementar listar_estados")


@app.get("/municipios", tags=["dados básicos"])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    """TODO: listar/buscar municípios, com filtros opcionais e paginação."""
    raise HTTPException(status_code=501, detail="TODO: implementar listar_municipios")


@app.get("/populacao/top-municipios", tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    """TODO: ranking dos municípios mais populosos."""
    raise HTTPException(status_code=501, detail="TODO: implementar top_municipios")


@app.get("/populacao/por-regiao", tags=["análise"])
def populacao_por_regiao():
    """TODO: população total agrupada por região."""
    raise HTTPException(status_code=501, detail="TODO: implementar populacao_por_regiao")


@app.get("/populacao/por-uf", tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    """TODO: população total por estado, com filtro opcional por região."""
    raise HTTPException(status_code=501, detail="TODO: implementar populacao_por_uf")


@app.get("/populacao/distribuicao", tags=["análise"])
def distribuicao_populacional():
    """TODO: valores de população de todos os municípios, para um histograma."""
    raise HTTPException(status_code=501, detail="TODO: implementar distribuicao_populacional")


@app.get("/populacao/dispersao-uf", tags=["análise"])
def dispersao_por_uf():
    """TODO: por estado, quantidade de municípios x população média, para um scatter."""
    raise HTTPException(status_code=501, detail="TODO: implementar dispersao_por_uf")


@app.get("/populacao/heatmap-regiao-porte", tags=["análise"])
def heatmap_regiao_porte():
    """TODO: quantidade de municípios por região x porte (pequeno/médio/grande),
    para um mapa de calor. Definam vocês os limites de população de cada porte."""
    raise HTTPException(status_code=501, detail="TODO: implementar heatmap_regiao_porte")


@app.get("/estatisticas/resumo", tags=["análise"])
def resumo_estatistico():
    """TODO: números resumo para os KPIs do topo do painel."""
    raise HTTPException(status_code=501, detail="TODO: implementar resumo_estatistico")


@app.get("/municipios/{id_municipio}", tags=["dados básicos"])
def detalhe_municipio(id_municipio: int):
    """TODO: dados completos de um município, ou 404 se não existir."""
    raise HTTPException(status_code=501, detail="TODO: implementar detalhe_municipio")


@app.post("/municipios", tags=["dados básicos"])
def criar_municipio():
    """TODO: cadastrar um novo município (nome, estado e população inicial).
    Como não existe um id_municipio real do IBGE pra um município novo,
    gerem um (por exemplo, MAX(id_municipio) + 1)."""
    raise HTTPException(status_code=501, detail="TODO: implementar criar_municipio")


@app.put("/municipios/{id_municipio}", tags=["dados básicos"])
def atualizar_municipio(id_municipio: int):
    """TODO: atualizar nome, estado e/ou população de um município existente."""
    raise HTTPException(status_code=501, detail="TODO: implementar atualizar_municipio")


@app.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):
    """TODO: remover um município (e os dados dependentes dele)."""
    raise HTTPException(status_code=501, detail="TODO: implementar remover_municipio")


# ---------------------------------------------------------------------------
# Cadastro: informações que o gestor registra sobre um município.
#
# Essa tabela não existe no banco original. Antes de implementar as rotas
# abaixo, decidam os campos que fazem sentido (status, prioridade,
# observação, responsável...) e criem a tabela no SQLite.
# ---------------------------------------------------------------------------

@app.post("/municipios/{id_municipio}/registros", tags=["cadastro"])
def criar_registro(id_municipio: int):
    """TODO: criar um novo registro de cadastro para o município."""
    raise HTTPException(status_code=501, detail="TODO: implementar criar_registro")


@app.get("/municipios/{id_municipio}/registros", tags=["cadastro"])
def listar_registros(id_municipio: int):
    """TODO: listar os registros de cadastro de um município."""
    raise HTTPException(status_code=501, detail="TODO: implementar listar_registros")


@app.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int):
    """TODO: atualizar um registro de cadastro existente."""
    raise HTTPException(status_code=501, detail="TODO: implementar atualizar_registro")


@app.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    """TODO: remover um registro de cadastro."""
    raise HTTPException(status_code=501, detail="TODO: implementar remover_registro")
