"""
Modelos Pydantic usados nas respostas da API.

Regiao já está pronto, como referência. Os demais modelos (para os
endpoints de análise e de cadastro) ficam por conta de vocês, conforme
forem implementando cada rota.
"""
from pydantic import BaseModel
from typing import Optional


class Regiao(BaseModel):
    id_regiao: int
    sigla_regiao: str
    nome_regiao: str

class LPMunicipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf:int

class LPEstado(BaseModel):
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


class LPResumoEstatistico(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: float
    ano_referencia: int
    municipio_mais_populoso: str
    uf_municipio_mais_populoso: str
    populacao_municipio_mais_populoso: float

class LPMunicipioPopulacao(BaseModel):
    nome_municipio: str
    sigla_uf: str
    valor: float

class LPPopulacaoPorRegiao(BaseModel):
    nome_regiao: str
    populacao: float

class LPPopulacaoPorEstado(BaseModel):
    nome_uf: str
    sigla_uf: str
    populacao: float

class LPDispersaoEstado(BaseModel):
    nome_uf: str
    sigla_uf: str
    nome_regiao: str
    qtd_municipios: int
    populacao_media: float

class LPHeatmapRegiaoPorte(BaseModel):
    nome_regiao: str
    porte: str
    quantidade: int

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


# ---- Análise --------------------------------------------------------------
class MunicipioMaisPopuloso(BaseModel):
    municipio: str
    uf: str
    populacao: int


class KPIs(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int
    ano_referencia: Optional[int] = None
    municipio_mais_populoso: Optional[MunicipioMaisPopuloso] = None


class MunicipioPopulacao(BaseModel):
    id_municipio: int
    municipio: str
    uf: str
    populacao: int


class RegiaoPopulacao(BaseModel):
    regiao: str
    populacao: int


class EstadoPopulacao(BaseModel):
    uf: str
    estado: str
    regiao: str
    populacao: int


class DispersaoEstado(BaseModel):
    uf: str
    estado: str
    regiao: str
    qtd_municipios: int
    populacao_media: float


class RegiaoPorte(BaseModel):
    regiao: str
    porte: str
    quantidade: int


class LPMunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: float

class LPMunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: float | None = None

class LPMunicipioComPopulacao(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: float

class LPRegistroGestorCreate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None

class LPRegistroGestorUpdate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None

class LPRegistroGestor(BaseModel):
    id_registro: int
    id_municipio: int
    status: str | None
    prioridade: str | None
    observacao: str | None
    responsavel: str | None
    data_registro: str

# ---- Município (dados básicos) — entrada ----------------------------------
class MunicipioCreate(BaseModel):
    nome: str
    uf: str
    populacao: int


class MunicipioUpdate(BaseModel):
    nome: str
    uf: str
    populacao: int


# ---- Cadastro (anotações do gestor) ---------------------------------------
class AcompanhamentoCreate(BaseModel):
    id_municipio: int
    status: str = "monitorando"
    prioridade: str = "media"
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


class AcompanhamentoUpdate(BaseModel):
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


class Acompanhamento(BaseModel):
    id: int
    id_municipio: int
    municipio: Optional[str] = None
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: Optional[str] = None
    atualizado_em: Optional[str] = None
