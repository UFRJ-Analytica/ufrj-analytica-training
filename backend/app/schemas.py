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
