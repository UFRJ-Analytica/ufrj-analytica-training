from pydantic import BaseModel

# Dados enviados para a API
class Municipio(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao_inicial: int


class Registro(BaseModel):
    status: str
    prioridade: str
    observacao: str
    responsavel: str

# Dados devolvidos pela API
class MunicipioOut(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int

    sigla_uf: str | None = None
    nome_uf: str | None = None
    id_regiao: int | None = None
    nome_regiao: str | None = None
    populacao: int | None = None
    ano: int | None = None 

class RegistroOut(BaseModel):
    id_registro: int
    id_municipio: int
    status: str
    prioridade: str
    observacao: str | None = None
    responsavel: str | None = None

# Dados básicos de consulta
class Regiao(BaseModel):
    id_regiao: int
    sigla_regiao: str
    nome_regiao: str

class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int