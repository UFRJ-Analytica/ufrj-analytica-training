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

# adicionados por leticia pessoa

class KpiResponse(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int 
    ano_referencia:int
    municipio_mais_populoso: str

class TopMunicipio(BaseModel):
    nome: str
    populacao:int

class PopulacaoPorRegiao(BaseModel):
    regiao: str
    populacao: int

class PopulacaoPorEstado(BaseModel):
    regiao: str
    estado: str
    populacao: int

class DispersaoMunicipioEstado(BaseModel):
    regiao: str
    estado: str
    quantidade_municipios: int
    populacao_media: float

class RegiaoPorte(BaseModel):
    regiao: str
    porte: str
    quantidade: int

# ---------------------------------------------------------------------------
# Municipios: informações que o gestor registra sobre um município.
# ---------------------------------------------------------------------------


class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int

class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None
    
class MunicipioResponse(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: int

# ---------------------------------------------------------------------------
# Cadastro: informações de gestão
# ---------------------------------------------------------------------------

class CadastroCreate(BaseModel):
    id_municipio: int
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None

class CadastroUpdate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None

class CadastroResponse(BaseModel):
    id_cadastro: int
    id_municipio: int
    status: str | None 
    prioridade: str | None 
    observacao: str | None 
    responsavel: str | None
    data_criacao: str | None
     