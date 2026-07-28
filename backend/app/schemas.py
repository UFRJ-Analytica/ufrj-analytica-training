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

class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int

class Municipio(BaseModel):
    id_municipio: int = 0
    nome_municipio: str
    id_uf: int

class MunicipioUpdate(BaseModel):
    id_municipio: int = 0
    nome_municipio: str = None
    id_uf: int = None

class CadastroMunicipal(BaseModel):
    status_atual: str
    prioridade: str
    responsavel: str
    id_municipio: int

class CadastroMunicipalUpdate(BaseModel):
    id_cadastro_municipal: int = 0
    status_atual: str = None
    prioridade: str = None
    responsavel: str = None
    id_municipio: int = None