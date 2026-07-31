"""
Modelos Pydantic usados nas respostas da API.

Regiao já está pronto, como referência. Os demais modelos (para os
endpoints de análise e de cadastro) ficam por conta de vocês, conforme
forem implementando cada rota.
"""
from pydantic import BaseModel


class Regiao(BaseModel):
    id_regiao: int
    sigla_regiao: str
    nome_regiao: str


class CriarMunicipioPayload(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao_inicial: int | None = None
    ano_referencia: int = 2022


class AtualizarMunicipioPayload(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None
    ano_referencia: int = 2022


class CriarRegistroPayload(BaseModel):
    status: str
    prioridade: str
    observacao: str | None = None
    responsavel: str | None = None


class AtualizarRegistroPayload(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None
