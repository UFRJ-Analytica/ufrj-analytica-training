from fastapi import APIRouter, HTTPException, Query
from app.schemas import (
    Municipio,
    Estado,
    Regiao,
    ResumoEstatistico,
    MunicipioPopulacao,
    PopulacaoPorRegiao,
    PopulacaoPorEstado,
    DispersaoEstado,
    HeatmapRegiaoPorte,
)

from app.database import query

router = APIRouter(prefix="/luiz-paulo", tags=["luiz_paulo"])

# Rota de teste
@router.get("/status")
def status():
    return {"status": "ok", "mensagem": "funcionando"}

@router.get("/estados", response_model=list[Estado])
def listar_estados():
    return query("SELECT id_uf, sigla_uf, nome_uf, id_regiao FROM estados")

@router.get("/regioes", response_model=list[Regiao])
def listar_regioes():
    return query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes")

@router.get("/municipios", response_model=list[Municipio])
def listar_municipios():
    return query("SELECT id_municipio, nome_municipio, id_uf FROM municipios")

@router.get("/municipios/{id_municipio}", response_model=Municipio)
def buscar_municipio(id_municipio: int):
    rows = query(
        "SELECT id_municipio, nome_municipio, id_uf FROM municipios WHERE id_municipio = ?",
        (id_municipio,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return rows[0]

#paineis de análise para streamlit

@router.get("/estatisticas/resumo", response_model=ResumoEstatistico) #KPIs
def resumo_estatistico():
    total_municipios = query("SELECT COUNT(*) AS total FROM municipios")[0]["total"]
    total_estados = query("SELECT COUNT(*) AS total FROM estados")[0]["total"]
    ano_referencia = query("SELECT MAX(ano) AS ano FROM populacao_municipal")[0]["ano"]
    populacao_total = query(
        "SELECT SUM(valor) AS total FROM populacao_municipal WHERE ano = ?",
        (ano_referencia,),
    )[0]["total"]
    mais_populoso = query(
        """
        SELECT m.nome_municipio, e.sigla_uf, p.valor
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = ?
        ORDER BY p.valor DESC
        LIMIT 1
        """,
        (ano_referencia,),
    )[0]

    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "ano_referencia": ano_referencia,
        "municipio_mais_populoso": mais_populoso["nome_municipio"],
        "uf_municipio_mais_populoso": mais_populoso["sigla_uf"],
        "populacao_municipio_mais_populoso": mais_populoso["valor"],
    }


@router.get("/populacao/top-municipios", response_model=list[MunicipioPopulacao]) #topN
def top_municipios(limit: int = Query(default=10, le=100)):
    return query(
        """
        SELECT m.nome_municipio, e.sigla_uf, p.valor
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        ORDER BY p.valor DESC
        LIMIT ?
        """,
        (limit,),
    )


@router.get("/populacao/por-regiao", response_model=list[PopulacaoPorRegiao]) #pop. regiao
def populacao_por_regiao():
    return query(
        """
        SELECT r.nome_regiao, SUM(p.valor) AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        GROUP BY r.nome_regiao
        ORDER BY populacao DESC
        """
    )


@router.get("/populacao/por-uf", response_model=list[PopulacaoPorEstado]) #pop. estado
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT e.nome_uf, e.sigla_uf, SUM(p.valor) AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
    """
    params: tuple = ()
    if id_regiao is not None:
        sql += " AND e.id_regiao = ?"
        params = (id_regiao,)
    sql += " GROUP BY e.nome_uf, e.sigla_uf ORDER BY populacao DESC"
    return query(sql, params)


@router.get("/populacao/distribuicao", response_model=list[MunicipioPopulacao]) #distr. pop.
def distribuicao_populacional():
    return query(
        """
        SELECT m.nome_municipio, e.sigla_uf, p.valor
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        """
    )


@router.get("/populacao/dispersao-uf", response_model=list[DispersaoEstado])
def dispersao_por_uf():
    return query(
        """
        SELECT e.nome_uf, e.sigla_uf, r.nome_regiao,
               COUNT(m.id_municipio) AS qtd_municipios,
               AVG(p.valor) AS populacao_media
        FROM municipios m
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        GROUP BY e.nome_uf, e.sigla_uf, r.nome_regiao
        ORDER BY qtd_municipios DESC
        """
    )


@router.get("/populacao/heatmap-regiao-porte", response_model=list[HeatmapRegiaoPorte])
def heatmap_regiao_porte():
    return query(
        """
        SELECT r.nome_regiao,
               CASE
                   WHEN p.valor <= 20000 THEN 'Pequeno'
                   WHEN p.valor BETWEEN 20001 AND 100000 THEN 'Médio'
                   ELSE 'Grande'
               END AS porte,
               COUNT(*) AS quantidade
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        GROUP BY r.nome_regiao, porte
        ORDER BY r.nome_regiao, porte
        """
    )