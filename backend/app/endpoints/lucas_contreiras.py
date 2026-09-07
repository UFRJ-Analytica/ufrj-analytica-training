"""
Endpoints de análise de vendas no Brasil para Lucas Contreiras.

Inclui endpoints para análise descritiva, estatísticas e operações CRUD
sobre dados de vendas, com suporte a filtros por região, estado e produto.
"""
import sqlite3
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel


DB_PATH = (
    Path(__file__).resolve().parents[3]
    / "entregaveis"
    / "banco_de_dados"
    / "lucas_contreiras_trainee"
    / "vendas.db"
)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute(sql: str, params: tuple = ()) -> None:
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


class VendaCreate(BaseModel):
    id_produto: int
    id_regiao: int
    quantidade: int
    valor_unitario: float
    desconto_pct: float = 0.0


class VendaUpdate(BaseModel):
    quantidade: int | None = None
    valor_unitario: float | None = None
    desconto_pct: float | None = None


router = APIRouter(
    prefix="/lucas-contreiras",
    tags=["Lucas Contreiras - Vendas"]
)


@router.get("/status")
def status():
    return {"status": "ok", "modulo": "Análise de Vendas"}


@router.get("/estatisticas/resumo")
def resumo_vendas():
    """Retorna resumo das estatísticas de vendas."""
    
    total_vendas = query("""
        SELECT COUNT(*) AS total
        FROM vendas
    """)

    valor_total = query("""
        SELECT ROUND(SUM(valor_total), 2) AS total
        FROM vendas
    """)

    desconto_total = query("""
        SELECT ROUND(SUM(desconto_valor), 2) AS total
        FROM vendas
    """)

    lucro_total = query("""
        SELECT ROUND(SUM(lucro_estimado), 2) AS total
        FROM vendas
    """)

    return {
        "total_vendas": total_vendas[0]["total"],
        "valor_total_vendido": valor_total[0]["total"],
        "desconto_concedido": desconto_total[0]["total"],
        "lucro_estimado": lucro_total[0]["total"]
    }


@router.get("/vendas/top-produtos")
def top_produtos(limit: int = Query(default=10, le=100)):
    """Retorna os produtos mais vendidos."""
    
    resultado = query("""
        SELECT
            p.id_produto,
            p.nome_produto,
            p.categoria,
            COUNT(*) AS quantidade_vendas,
            ROUND(SUM(v.quantidade), 2) AS quantidade_total,
            ROUND(SUM(v.valor_total), 2) AS receita_total,
            ROUND(AVG(v.valor_unitario), 2) AS preco_medio
        FROM vendas v
        JOIN produtos p ON v.id_produto = p.id_produto
        GROUP BY p.id_produto, p.nome_produto, p.categoria
        ORDER BY receita_total DESC
        LIMIT ?
    """, (limit,))
    
    return resultado


@router.get("/vendas/por-regiao")
def vendas_por_regiao():
    """Análise de vendas agrupadas por região."""
    
    resultado = query("""
        SELECT
            r.id_regiao,
            r.nome_regiao,
            COUNT(*) AS quantidade_vendas,
            ROUND(SUM(v.quantidade), 0) AS quantidade_total,
            ROUND(SUM(v.valor_total), 2) AS valor_total,
            ROUND(AVG(v.lucro_estimado), 2) AS lucro_medio
        FROM vendas v
        JOIN regioes r ON v.id_regiao = r.id_regiao
        GROUP BY r.id_regiao, r.nome_regiao
        ORDER BY valor_total DESC
    """)
    
    return resultado


@router.get("/vendas/por-categoria")
def vendas_por_categoria():
    """Análise de vendas agrupadas por categoria de produto."""
    
    resultado = query("""
        SELECT
            p.categoria,
            COUNT(*) AS quantidade_vendas,
            ROUND(SUM(v.quantidade), 0) AS unidades_vendidas,
            ROUND(SUM(v.valor_total), 2) AS receita,
            ROUND(SUM(v.desconto_valor), 2) AS desconto_total,
            ROUND(SUM(v.lucro_estimado), 2) AS lucro_total,
            ROUND(AVG(v.valor_unitario), 2) AS preco_medio
        FROM vendas v
        JOIN produtos p ON v.id_produto = p.id_produto
        GROUP BY p.categoria
        ORDER BY receita DESC
    """)
    
    return resultado


@router.get("/vendas/desempenho-temporal")
def desempenho_temporal():
    """Análise de desempenho ao longo do tempo."""
    
    resultado = query("""
        SELECT
            DATE(data_venda) AS data,
            COUNT(*) AS quantidade_vendas,
            ROUND(SUM(v.valor_total), 2) AS valor_diario,
            ROUND(SUM(v.lucro_estimado), 2) AS lucro_diario,
            ROUND(AVG(v.desconto_pct), 2) AS desconto_medio_pct
        FROM vendas v
        GROUP BY DATE(data_venda)
        ORDER BY data DESC
    """)
    
    return resultado


@router.get("/vendas/margem-lucro")
def analise_margem_lucro():
    """Análise de margem de lucro por produto."""
    
    resultado = query("""
        SELECT
            p.nome_produto,
            p.categoria,
            ROUND(AVG((v.lucro_estimado / v.valor_total) * 100), 2) AS margem_lucro_pct,
            COUNT(*) AS quantidade_vendas,
            ROUND(SUM(v.lucro_estimado), 2) AS lucro_total
        FROM vendas v
        JOIN produtos p ON v.id_produto = p.id_produto
        WHERE v.valor_total > 0
        GROUP BY p.id_produto, p.nome_produto, p.categoria
        ORDER BY margem_lucro_pct DESC
    """)
    
    return resultado


@router.get("/vendas/impacto-desconto")
def impacto_desconto():
    """Análise do impacto de descontos nas vendas."""
    
    resultado = query("""
        SELECT
            CASE
                WHEN v.desconto_pct = 0 THEN 'Sem desconto'
                WHEN v.desconto_pct <= 5 THEN '1-5%'
                WHEN v.desconto_pct <= 10 THEN '6-10%'
                WHEN v.desconto_pct <= 15 THEN '11-15%'
                ELSE 'Acima de 15%'
            END AS faixa_desconto,
            COUNT(*) AS quantidade_vendas,
            ROUND(AVG(v.quantidade), 2) AS quantidade_media,
            ROUND(SUM(v.valor_total), 2) AS valor_total,
            ROUND(SUM(v.desconto_valor), 2) AS desconto_concedido,
            ROUND(SUM(v.lucro_estimado), 2) AS lucro_total
        FROM vendas v
        GROUP BY faixa_desconto
        ORDER BY quantidade_vendas DESC
    """)
    
    return resultado


@router.get("/vendas")
def listar_vendas(
    id_regiao: int | None = Query(default=None),
    id_produto: int | None = Query(default=None),
    limit: int = Query(default=50, le=500)
):
    """Lista vendas com filtros opcionais."""
    
    sql = """
        SELECT
            v.id_venda,
            v.data_venda,
            p.nome_produto,
            p.categoria,
            r.nome_regiao,
            v.quantidade,
            v.valor_unitario,
            v.desconto_pct,
            v.valor_total,
            v.lucro_estimado
        FROM vendas v
        JOIN produtos p ON v.id_produto = p.id_produto
        JOIN regioes r ON v.id_regiao = r.id_regiao
        WHERE 1=1
    """
    
    params = []
    
    if id_regiao is not None:
        sql += " AND v.id_regiao = ?"
        params.append(id_regiao)
    
    if id_produto is not None:
        sql += " AND v.id_produto = ?"
        params.append(id_produto)
    
    sql += " ORDER BY v.data_venda DESC LIMIT ?"
    params.append(limit)
    
    return query(sql, tuple(params))


@router.get("/vendas/{id_venda}")
def detalhe_venda(id_venda: int):
    """Retorna detalhes de uma venda específica."""
    
    resultado = query("""
        SELECT
            v.id_venda,
            v.data_venda,
            p.nome_produto,
            p.categoria,
            r.nome_regiao,
            v.quantidade,
            v.valor_unitario,
            v.desconto_pct,
            v.desconto_valor,
            v.valor_total,
            v.custo_estimado,
            v.lucro_estimado
        FROM vendas v
        JOIN produtos p ON v.id_produto = p.id_produto
        JOIN regioes r ON v.id_regiao = r.id_regiao
        WHERE v.id_venda = ?
    """, (id_venda,))
    
    if not resultado:
        raise HTTPException(
            status_code=404,
            detail="Venda não encontrada."
        )
    
    return resultado[0]


@router.post("/vendas")
def criar_venda(venda: VendaCreate):
    """Cria uma nova venda."""
    
    # Verifica se produto e região existem
    produto = query("SELECT preco_unitario FROM produtos WHERE id_produto = ?", (venda.id_produto,))
    regiao = query("SELECT id_regiao FROM regioes WHERE id_regiao = ?", (venda.id_regiao,))
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    if not regiao:
        raise HTTPException(status_code=404, detail="Região não encontrada.")
    
    # Cálculos
    valor_bruto = venda.valor_unitario * venda.quantidade
    desconto_valor = valor_bruto * (venda.desconto_pct / 100)
    valor_total = valor_bruto - desconto_valor
    custo_estimado = valor_total * 0.4  # Estimativa de 40% de custo
    lucro_estimado = valor_total - custo_estimado
    
    execute("""
        INSERT INTO vendas (
            id_produto,
            id_regiao,
            quantidade,
            valor_unitario,
            desconto_pct,
            desconto_valor,
            valor_total,
            custo_estimado,
            lucro_estimado,
            data_venda
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        venda.id_produto,
        venda.id_regiao,
        venda.quantidade,
        venda.valor_unitario,
        venda.desconto_pct,
        desconto_valor,
        valor_total,
        custo_estimado,
        lucro_estimado
    ))
    
    return {
        "mensagem": "Venda criada com sucesso.",
        "valor_total": valor_total,
        "lucro_estimado": lucro_estimado
    }


@router.put("/vendas/{id_venda}")
def atualizar_venda(id_venda: int, venda: VendaUpdate):
    """Atualiza dados de uma venda."""
    
    existente = query("SELECT id_venda FROM vendas WHERE id_venda = ?", (id_venda,))
    
    if not existente:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")
    
    campos = []
    params = []
    
    if venda.quantidade is not None:
        campos.append("quantidade = ?")
        params.append(venda.quantidade)
    
    if venda.valor_unitario is not None:
        campos.append("valor_unitario = ?")
        params.append(venda.valor_unitario)
    
    if venda.desconto_pct is not None:
        campos.append("desconto_pct = ?")
        params.append(venda.desconto_pct)
    
    if campos:
        params.append(id_venda)
        execute(
            f"UPDATE vendas SET {', '.join(campos)} WHERE id_venda = ?",
            tuple(params)
        )
    
    return {"mensagem": "Venda atualizada com sucesso."}


@router.delete("/vendas/{id_venda}")
def remover_venda(id_venda: int):
    """Remove uma venda."""
    
    existente = query("SELECT id_venda FROM vendas WHERE id_venda = ?", (id_venda,))
    
    if not existente:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")
    
    execute("DELETE FROM vendas WHERE id_venda = ?", (id_venda,))
    
    return {"mensagem": "Venda removida com sucesso."}


@router.get("/produtos")
def listar_produtos(limit: int = Query(default=50, le=500)):
    """Lista produtos disponíveis."""
    
    return query("""
        SELECT
            id_produto,
            nome_produto,
            categoria,
            preco_unitario,
            custo_unitario
        FROM produtos
        ORDER BY nome_produto
        LIMIT ?
    """, (limit,))


@router.get("/regioes")
def listar_regioes():
    """Lista regiões disponíveis."""
    
    return query("""
        SELECT
            id_regiao,
            nome_regiao,
            sigla_regiao
        FROM regioes
        ORDER BY nome_regiao
    """)
