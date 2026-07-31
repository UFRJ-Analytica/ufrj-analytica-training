-- queries.sql
-- Consultas SQL obrigatórias para exploração, validação e manipulação de dados
-- Autor: Lucas Contreiras

-- Q1: Listar todas as regiões
SELECT * FROM regioes;

-- Q2: Listar todos os estados de uma região específica
SELECT e.id_uf, e.nome_uf, e.sigla_uf, r.nome_regiao
FROM estados e
JOIN regioes r ON e.id_regiao = r.id_regiao
WHERE r.nome_regiao = 'Sudeste'
ORDER BY e.nome_uf;

-- Q3: Listar todos os municípios de um estado específico
SELECT m.id_municipio, m.nome_municipio, e.nome_uf, e.sigla_uf
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
WHERE e.sigla_uf = 'SP'
ORDER BY m.nome_municipio;

-- Q4: Mostrar estado e região para cada município (com população)
SELECT m.id_municipio, m.nome_municipio, e.nome_uf, e.sigla_uf, r.nome_regiao,
       COALESCE(fi.valor, 0) AS populacao
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
ORDER BY r.nome_regiao, e.nome_uf, m.nome_municipio;

-- Q5: Mostrar dados de população estimada com detalhes
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao,
       i.nome_indicador, fi.valor, fi.ano
FROM fato_indicador_municipal fi
JOIN municipios m ON fi.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
JOIN indicadores i ON fi.id_indicador = i.id_indicador
WHERE i.nome_indicador LIKE '%população%'
ORDER BY fi.ano DESC, m.nome_municipio;

-- Q6: Contar quantidade de municípios por estado
SELECT e.nome_uf, e.sigla_uf, COUNT(m.id_municipio) AS total_municipios
FROM estados e
LEFT JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.nome_uf, e.sigla_uf
ORDER BY total_municipios DESC;

-- Q7: Contar quantidade de municípios por região
SELECT r.nome_regiao, COUNT(DISTINCT m.id_municipio) AS total_municipios
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY total_municipios DESC;

-- Q8: Total de população por estado (agregação)
SELECT e.nome_uf, e.sigla_uf, SUM(fi.valor) AS populacao_total
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
GROUP BY e.id_uf, e.nome_uf, e.sigla_uf
ORDER BY populacao_total DESC;

-- Q9: Top 10 estados com maior quantidade de municípios
SELECT e.nome_uf, e.sigla_uf, COUNT(m.id_municipio) AS total_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.nome_uf, e.sigla_uf
ORDER BY total_municipios DESC
LIMIT 10;

-- Q10: Demonstração de DML - Criar tabela de teste, inserir, atualizar e deletar
CREATE TABLE IF NOT EXISTS teste_municipio_lucas (
    id_teste INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_municipio TEXT NOT NULL,
    sigla_uf TEXT NOT NULL,
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO teste_municipio_lucas (nome_municipio, sigla_uf) VALUES ('Municipio Teste', 'XX');

UPDATE teste_municipio_lucas SET nome_municipio = 'Municipio Teste Atualizado' WHERE id_teste = 1;

DELETE FROM teste_municipio_lucas WHERE id_teste = 1;

SELECT * FROM teste_municipio_lucas;
