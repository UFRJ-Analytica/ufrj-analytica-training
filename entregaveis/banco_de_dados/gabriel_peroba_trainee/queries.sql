-- Questao 1 
SELECT 
    id_regiao, 
    sigla_regiao, 
    nome_regiao 
FROM regioes;

-- Questao 2 
SELECT 
    id_uf, 
    sigla_uf, 
    nome_uf 
FROM estados 
WHERE id_regiao = 3;

-- Questao 3 
SELECT 
    id_municipio, 
    nome_municipio 
FROM municipios 
WHERE id_uf = 33;

-- Questao 4
SELECT 
    m.nome_municipio, 
    e.nome_uf, 
    e.sigla_uf, 
    r.nome_regiao 
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao;

-- Questao 5
SELECT 
    m.nome_municipio, 
    e.sigla_uf, 
    r.nome_regiao, 
    p.ano, 
    p.valor AS populacao_estimada
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao;

-- Questao 6
SELECT 
    e.sigla_uf, 
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.sigla_uf
ORDER BY qtd_municipios DESC;

-- Questao 7
SELECT 
    r.nome_regiao, 
    COUNT(m.id_municipio) AS qtd_municipios
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY r.nome_regiao
ORDER BY qtd_municipios DESC;

-- Questao 8
SELECT 
    e.sigla_uf, 
    SUM(p.valor) AS populacao_total
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
GROUP BY e.sigla_uf
ORDER BY populacao_total DESC;

-- Questao 9
SELECT 
    e.sigla_uf, 
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.sigla_uf
ORDER BY qtd_municipios DESC
LIMIT 10;

-- Questao 10

-- 10.1
CREATE TABLE tabela_teste (
    id_teste INTEGER PRIMARY KEY,
    descricao TEXT,
    status TEXT
);

-- 10.2 
INSERT INTO tabela_teste (id_teste, descricao, status) 
VALUES (1, 'Primeiro teste de inserção', 'Pendente');

-- 10.3 
UPDATE tabela_teste 
SET status = 'Concluído' 
WHERE id_teste = 1;

-- 10.4 
DELETE FROM tabela_teste 
WHERE id_teste = 1;

DROP TABLE tabela_teste;