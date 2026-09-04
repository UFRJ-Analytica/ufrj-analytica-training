"""
Modelos Pydantic usados nas respostas da API.

Regiao já está pronto, como referência. Os demais modelos (para os
endpoints de análise e de cadastro) ficam por conta de vocês, conforme
forem implementando cada rota.
"""
from pydantic import BaseModel, Field
from typing import Optional

class Regiao(BaseModel):
    id_regiao: int
    sigla_regiao: str
    nome_regiao: str

class ResumoEstatistico(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int
    ano_referencia: int
    municipio_mais_populoso: str

class TopMunicipio(BaseModel):
    nome_municipio: str
    sigla_uf: str
    populacao: int

class PopulacaoRegiao(BaseModel):
    nome_regiao: str
    populacao_total: int

class PopulacaoUF(BaseModel):
    sigla_uf: str
    populacao_total: int

class DistribuicaoPopulacao(BaseModel):
    nome_municipio: str
    populacao: int

class DispersaoUF(BaseModel):
    sigla_uf: str
    id_regiao: int
    qtd_municipios: int
    media_populacao: float

class HeatmapPorte(BaseModel):
    nome_regiao: str
    porte: str
    quantidade: int

class MunicipioBase(BaseModel):
    nome_municipio: str
    id_uf: int

class Municipio(MunicipioBase):
    id_municipio: int

class MunicipioCreate(MunicipioBase):
    populacao_inicial: int = Field(..., gt=0)

class MunicipioUpdate(BaseModel):
    nome_municipio: Optional[str] = None
    id_uf: Optional[int] = None
    populacao: Optional[int] = Field(None, gt=0)

class DetalheMunicipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    sigla_uf: str
    nome_regiao: str
    populacao: int
    ano_referencia: int

# Modelos para o Cadastro
class RegistroBase(BaseModel):
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: str

class RegistroCreate(RegistroBase):
    pass

class RegistroUpdate(BaseModel):
    status: Optional[str] = None
    prioridade: Optional[str] = None
    observacao: Optional[str] = None
    responsavel: Optional[str] = None

class Registro(RegistroBase):
    id_registro: int
    id_municipio: int