"""
Script de inicialização do banco de dados de vendas para Lucas Contreiras.
Cria tabelas e insere dados de exemplo.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

# Caminho do banco
db_dir = Path(__file__).resolve().parent.parent / "banco_de_dados" / "lucas_contreiras_trainee"
db_dir.mkdir(parents=True, exist_ok=True)
db_path = db_dir / "vendas.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tabela de Regiões
cursor.execute("""
    CREATE TABLE IF NOT EXISTS regioes (
        id_regiao INTEGER PRIMARY KEY,
        nome_regiao TEXT NOT NULL,
        sigla_regiao TEXT NOT NULL
    )
""")

# Tabela de Produtos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id_produto INTEGER PRIMARY KEY,
        nome_produto TEXT NOT NULL,
        categoria TEXT NOT NULL,
        preco_unitario REAL NOT NULL,
        custo_unitario REAL NOT NULL
    )
""")

# Tabela de Vendas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produto INTEGER NOT NULL,
        id_regiao INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        valor_unitario REAL NOT NULL,
        desconto_pct REAL DEFAULT 0,
        desconto_valor REAL,
        valor_total REAL,
        custo_estimado REAL,
        lucro_estimado REAL,
        data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
        FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
    )
""")

# Limpar dados existentes
cursor.execute("DELETE FROM regioes")
cursor.execute("DELETE FROM produtos")
cursor.execute("DELETE FROM vendas")

# Inserir regiões
regioes = [
    (1, "Norte", "N"),
    (2, "Nordeste", "NE"),
    (3, "Centro-Oeste", "CO"),
    (4, "Sudeste", "SE"),
    (5, "Sul", "S")
]
cursor.executemany("INSERT INTO regioes VALUES (?, ?, ?)", regioes)

# Inserir produtos
produtos = [
    (1, "Eletrônicos Premium", "Eletrônicos", 2500.00, 1000.00),
    (2, "Smartphone X", "Eletrônicos", 1200.00, 400.00),
    (3, "Tablet Pro", "Eletrônicos", 800.00, 300.00),
    (4, "Notebook Gamer", "Informática", 3500.00, 1400.00),
    (5, "Monitor 4K", "Informática", 1500.00, 600.00),
    (6, "Teclado Mecânico", "Periféricos", 350.00, 100.00),
    (7, "Mouse Wireless", "Periféricos", 120.00, 30.00),
    (8, "Headphone Noise Cancelling", "Áudio", 450.00, 150.00),
    (9, "Webcam HD", "Periféricos", 280.00, 80.00),
    (10, "Carregador Rápido", "Acessórios", 80.00, 20.00)
]
cursor.executemany("INSERT INTO produtos VALUES (?, ?, ?, ?, ?)", produtos)

# Gerar vendas de exemplo (últimos 30 dias)
vendas = []
for _ in range(150):
    id_produto = random.randint(1, 10)
    id_regiao = random.randint(1, 5)
    quantidade = random.randint(1, 20)
    desconto_pct = random.choice([0, 5, 10, 15, 20])
    dias_atras = random.randint(0, 30)
    data_venda = (datetime.now() - timedelta(days=dias_atras)).isoformat()
    
    # Buscar produto
    cursor.execute("SELECT preco_unitario, custo_unitario FROM produtos WHERE id_produto = ?", (id_produto,))
    preco, custo = cursor.fetchone()
    
    valor_unitario = preco * random.uniform(0.9, 1.1)  # Variação no preço
    valor_bruto = valor_unitario * quantidade
    desconto_valor = valor_bruto * (desconto_pct / 100)
    valor_total = valor_bruto - desconto_valor
    custo_estimado = custo * quantidade
    lucro_estimado = valor_total - custo_estimado
    
    vendas.append((
        id_produto, id_regiao, quantidade, valor_unitario,
        desconto_pct, desconto_valor, valor_total, custo_estimado,
        lucro_estimado, data_venda
    ))

cursor.executemany("""
    INSERT INTO vendas (
        id_produto, id_regiao, quantidade, valor_unitario,
        desconto_pct, desconto_valor, valor_total, custo_estimado,
        lucro_estimado, data_venda
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", vendas)

conn.commit()
conn.close()

print(f"✓ Banco de dados criado em: {db_path}")
print(f"✓ Regiões: {len(regioes)}")
print(f"✓ Produtos: {len(produtos)}")
print(f"✓ Vendas de exemplo: {len(vendas)}")
