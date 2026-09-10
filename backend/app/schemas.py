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
    nome_uf: str
    sigla_uf: str
    id_regiao: int

class Municipio(BaseModel):
    nome_municipio: str
    nome_uf: str
    populacao: int

class Populacao(BaseModel):
    nome: str
    total: int

class Dispersao(BaseModel):
    nome: str
    media: float
    quant: int
    id_regiao: int

class PorteRegiao(BaseModel):
    nome_regiao: str
    pequeno: int
    medio: int
    grande: int

class MedidasResumo(BaseModel):
    municipios: int
    estados: int
    populacao_total: int
    ano: int
    maior_municipio: str

class DetalheMunicipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    valor: int

class Registro(BaseModel):
    id_registro: int
    id_municipio: int
    observacao: str
    responsavel: str