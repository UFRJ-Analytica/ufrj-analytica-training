-- queries.sql
-- Consultas obrigatorias sobre o modelo normalizado.
-- Cobre SELECT, WHERE, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

PRAGMA foreign_keys = ON;

-- 1. Todas as regioes cadastradas.
SELECT id_regiao, sigla_regiao, nome_regiao
FROM regioes
ORDER BY nome_regiao;

-- 2. Estados de uma regiao especifica (Sudeste).
SELECT e.id_uf, e.sigla_uf, e.nome_uf
FROM estados e
JOIN regioes r ON r.id_regiao = e.id_regiao
WHERE r.nome_regiao = 'Sudeste'
ORDER BY e.nome_uf;

-- 3. Municipios de uma UF especifica (Rio de Janeiro).
SELECT m.id_municipio, m.nome_municipio
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
WHERE e.sigla_uf = 'RJ'
ORDER BY m.nome_municipio;

-- 4. Estado e regiao de cada municipio (join encadeado municipio -> estado -> regiao).
SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
ORDER BY m.nome_municipio
LIMIT 20;

-- 5. Populacao estimada dos municipios, com UF e regiao.
SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    p.ano,
    p.valor AS populacao_estimada
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
ORDER BY p.valor DESC
LIMIT 20;

-- 6. Quantidade de municipios por estado.
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
LEFT JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC;

-- 7. Quantidade de municipios por regiao.
SELECT
    r.nome_regiao,
    COUNT(m.id_municipio) AS qtd_municipios
FROM regioes r
JOIN estados e ON e.id_regiao = r.id_regiao
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY qtd_municipios DESC;

-- 8. Populacao total estimada por estado.
SELECT
    e.sigla_uf,
    e.nome_uf,
    SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_total DESC;

-- 9. Top 10 estados por quantidade de municipios.
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC
LIMIT 10;

-- 10. Demonstracao de INSERT, UPDATE e DELETE em uma tabela auxiliar de teste,
--     sem tocar nas tabelas finais do modelo.
DROP TABLE IF EXISTS teste_operacoes;

CREATE TABLE teste_operacoes (
    id_teste   INTEGER PRIMARY KEY,
    observacao TEXT NOT NULL
);

INSERT INTO teste_operacoes (id_teste, observacao)
VALUES (1, 'Registro criado para validar INSERT');

UPDATE teste_operacoes
SET observacao = 'Registro atualizado para validar UPDATE'
WHERE id_teste = 1;

SELECT * FROM teste_operacoes;

DELETE FROM teste_operacoes
WHERE id_teste = 1;

SELECT COUNT(*) AS linhas_restantes FROM teste_operacoes;
