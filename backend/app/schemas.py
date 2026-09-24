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

class Municipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf:int

class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int

class Populacao_Municipal(BaseModel):
    id_municipio: int
    ano: int
    indicador: str
    valor: float
    unidade:str
    fonte: str


class ResumoEstatistico(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: float
    ano_referencia: int
    municipio_mais_populoso: str
    uf_municipio_mais_populoso: str
    populacao_municipio_mais_populoso: float

class MunicipioPopulacao(BaseModel):
    nome_municipio: str
    sigla_uf: str
    valor: float

class PopulacaoPorRegiao(BaseModel):
    nome_regiao: str
    populacao: float

class PopulacaoPorEstado(BaseModel):
    nome_uf: str
    sigla_uf: str
    populacao: float

class DispersaoEstado(BaseModel):
    nome_uf: str
    sigla_uf: str
    nome_regiao: str
    qtd_municipios: int
    populacao_media: float

class HeatmapRegiaoPorte(BaseModel):
    nome_regiao: str
    porte: str
    quantidade: int

