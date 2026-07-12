-- queries.sql — 10 consultas obrigatórias
-- Modelo: regioes, estados(id_uf), municipios(id_uf), populacao_municipal.
-- Cobre SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

PRAGMA foreign_keys = ON;

-- 1. Quais regiões existem na base?
SELECT id_regiao, sigla_regiao, nome_regiao
FROM regioes
ORDER BY nome_regiao;

-- 2. Quais estados pertencem a uma região escolhida? (ex.: Sudeste)
SELECT e.sigla_uf, e.nome_uf
FROM estados e
JOIN regioes r ON r.id_regiao = e.id_regiao
WHERE r.nome_regiao = 'Sudeste'
ORDER BY e.nome_uf;

-- 3. Quais municípios pertencem a uma UF escolhida? (ex.: RJ)
SELECT m.nome_municipio
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
WHERE e.sigla_uf = 'RJ'
ORDER BY m.nome_municipio;

-- 4. Qual é o estado e a região de cada município?
SELECT m.nome_municipio, e.sigla_uf, r.nome_regiao
FROM municipios m
JOIN estados e ON e.id_uf     = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
ORDER BY r.nome_regiao, e.sigla_uf, m.nome_municipio;

-- 5. População estimada dos municípios (município, UF, região, ano, valor).
SELECT m.nome_municipio, e.sigla_uf, r.nome_regiao, p.ano, p.valor
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
JOIN regioes    r ON r.id_regiao    = e.id_regiao
ORDER BY p.valor DESC;

-- 6. Quantos municípios existem por estado?
SELECT e.sigla_uf, e.nome_uf, COUNT(*) AS qtd_municipios
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC;

-- 7. Quantos municípios existem por região?
SELECT r.nome_regiao, COUNT(*) AS qtd_municipios
FROM municipios m
JOIN estados e ON e.id_uf     = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY qtd_municipios DESC;

-- 8. População total estimada por estado.
SELECT e.sigla_uf, e.nome_uf, SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_total DESC;

-- 9. Top 10 estados por quantidade de municípios.
SELECT e.sigla_uf, e.nome_uf, COUNT(*) AS qtd_municipios
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC
LIMIT 10;

-- 10. Tabela de teste com INSERT + UPDATE + DELETE.
DROP TABLE IF EXISTS teste_operacoes;
CREATE TABLE teste_operacoes (
    id    INTEGER PRIMARY KEY,
    nome  TEXT NOT NULL,
    valor INTEGER
);

-- INSERT: adiciona dois registros
INSERT INTO teste_operacoes (id, nome, valor) VALUES (1, 'Registro A', 100);
INSERT INTO teste_operacoes (id, nome, valor) VALUES (2, 'Registro B', 200);
SELECT 'apos INSERT' AS etapa, id, nome, valor FROM teste_operacoes ORDER BY id;

-- UPDATE: altera o valor do registro 1
UPDATE teste_operacoes SET valor = 999 WHERE id = 1;
SELECT 'apos UPDATE' AS etapa, id, nome, valor FROM teste_operacoes ORDER BY id;

-- DELETE: remove o registro 2
DELETE FROM teste_operacoes WHERE id = 2;
SELECT 'apos DELETE' AS etapa, id, nome, valor FROM teste_operacoes ORDER BY id;

-- limpeza da tabela de teste (não faz parte do modelo final)
DROP TABLE teste_operacoes;
