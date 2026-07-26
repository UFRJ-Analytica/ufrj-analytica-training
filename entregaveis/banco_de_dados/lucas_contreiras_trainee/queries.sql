-- queries.sql
-- Consultas SQL obrigatórias para exploração, validação e manipulação de dados
-- Autor: Lucas Contreiras

-- Q1: Listar todas as regiões
SELECT * FROM regioes;

-- Q2: Listar todos os estados de uma região específica
SELECT e.id_estado, e.nome_estado, e.uf, r.nome_regiao
FROM estados e
JOIN regioes r ON e.id_regiao = r.id_regiao
WHERE r.nome_regiao = 'Sudeste'
ORDER BY e.nome_estado;

-- Q3: Listar todos os municípios de um estado específico
SELECT m.id_municipio, m.nome_municipio, e.nome_estado, e.uf
FROM municipios m
JOIN estados e ON m.id_estado = e.id_estado
WHERE e.uf = 'SP'
ORDER BY m.nome_municipio;

-- Q4: Mostrar estado e região para cada município (com população)
SELECT m.id_municipio, m.nome_municipio, e.nome_estado, e.uf, r.nome_regiao, 
       COALESCE(fi.valor_populacao_estimada, 0) AS populacao
FROM municipios m
JOIN estados e ON m.id_estado = e.id_estado
JOIN regioes r ON e.id_regiao = r.id_regiao
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
ORDER BY r.nome_regiao, e.nome_estado, m.nome_municipio;

-- Q5: Mostrar dados de população estimada com detalhes
SELECT m.nome_municipio, e.nome_estado, r.nome_regiao, 
       i.nome_indicador, fi.valor_populacao_estimada, fi.ano_referencia
FROM fato_indicador_municipal fi
JOIN municipios m ON fi.id_municipio = m.id_municipio
JOIN estados e ON m.id_estado = e.id_estado
JOIN regioes r ON e.id_regiao = r.id_regiao
JOIN indicadores i ON fi.id_indicador = i.id_indicador
WHERE i.nome_indicador LIKE '%população%'
ORDER BY fi.ano_referencia DESC, m.nome_municipio;

-- Q6: Contar quantidade de municípios por estado
SELECT e.nome_estado, e.uf, COUNT(m.id_municipio) AS total_municipios
FROM estados e
LEFT JOIN municipios m ON e.id_estado = m.id_estado
GROUP BY e.id_estado, e.nome_estado, e.uf
ORDER BY total_municipios DESC;

-- Q7: Contar quantidade de municípios por região
SELECT r.nome_regiao, COUNT(DISTINCT m.id_municipio) AS total_municipios
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_estado = m.id_estado
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY total_municipios DESC;

-- Q8: Total de população por estado (agregação)
SELECT e.nome_estado, e.uf, SUM(fi.valor_populacao_estimada) AS populacao_total
FROM estados e
JOIN municipios m ON e.id_estado = m.id_estado
LEFT JOIN fato_indicador_municipal fi ON m.id_municipio = fi.id_municipio
GROUP BY e.id_estado, e.nome_estado, e.uf
ORDER BY populacao_total DESC;

-- Q9: Top 10 estados com maior quantidade de municípios
SELECT TOP 10 e.nome_estado, e.uf, COUNT(m.id_municipio) AS total_municipios
FROM estados e
JOIN municipios m ON e.id_estado = m.id_estado
GROUP BY e.id_estado, e.nome_estado, e.uf
ORDER BY total_municipios DESC;

-- Q10: Demonstração de DML - Criar tabela de teste, inserir, atualizar e deletar
-- Criar tabela de teste
CREATE TABLE IF NOT EXISTS teste_municipio (
    id_teste INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_municipio TEXT NOT NULL,
    uf TEXT NOT NULL,
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Inserir registro de teste
INSERT INTO teste_municipio (nome_municipio, uf) VALUES ('Município Teste', 'XX');

-- Atualizar registro de teste
UPDATE teste_municipio SET nome_municipio = 'Município Teste Atualizado' WHERE id_teste = 1;

-- Deletar registro de teste
DELETE FROM teste_municipio WHERE id_teste = 1;

-- Verificar que a tabela está vazia (ou contém apenas registros anteriores)
SELECT * FROM teste_municipio;
