"""Indicadores populacionais específicos do painel do Luiz Conti."""

from fastapi import APIRouter, Query

from app.database import query

router = APIRouter(prefix="/luiz-conti", tags=["Luiz Conti - População"])


@router.get("/status")
def status() -> dict[str, str]:
    return {"status": "ok", "modulo": "Painel populacional"}


@router.get("/kpis")
def kpis() -> dict:
    rows = query(
        """
        SELECT
            (SELECT COUNT(*) FROM municipios) AS municipios,
            (SELECT COUNT(*) FROM estados) AS estados,
            (SELECT COUNT(*) FROM regioes) AS regioes,
            (SELECT COALESCE(SUM(valor), 0) FROM fato_indicador_municipal) AS populacao,
            (SELECT MAX(ano) FROM fato_indicador_municipal) AS ano
        """
    )
    return rows[0]


@router.get("/destaques")
def destaques(limite: int = Query(default=10, ge=1, le=50)) -> list[dict]:
    return query(
        """
        SELECT m.nome_municipio, e.sigla_uf, r.nome_regiao,
               f.valor AS populacao, f.ano
        FROM fato_indicador_municipal f
        JOIN municipios m ON m.id_municipio = f.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        ORDER BY f.valor DESC
        LIMIT ?
        """,
        (limite,),
    )
