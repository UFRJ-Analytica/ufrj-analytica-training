-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1. Quais regiões existem na base?
SELECT 
    id_regiao, 
    nome_regiao, 
    sigla_regiao 
FROM regioes;

-- 2. Quais estados pertencem a uma região escolhida?
-- Região Sul (id_regiao = 4) como exemplo.
SELECT 
    nome_uf, 
    sigla_uf 
FROM estados 
WHERE id_regiao = 4;

-- 3. Quais municípios pertencem a uma UF escolhida?
-- Estado do Rio de Janeiro (id_uf = 33) como exemplo.
SELECT 
    id_municipio, 
    nome_municipio 
FROM municipios 
WHERE id_uf = 33;

-- 4. Qual é o estado e a região de cada município?
SELECT 
    m.nome_municipio, 
    e.nome_uf AS estado, 
    r.nome_regiao AS regiao
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
-- Ano específico (2021) 
SELECT 
    m.nome_municipio, 
    e.sigla_uf AS UF, 
    r.nome_regiao AS regiao, 
    p.ano, 
    p.valor AS populacao_estimada
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
WHERE p.ano = 2021;

-- 6. Quantos municípios existem por estado?
SELECT 
    e.nome_uf, 
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf
ORDER BY quantidade_municipios DESC;

-- 7. Quantos municípios existem por região?
SELECT 
    r.nome_regiao, 
    COUNT(m.id_municipio) AS quantidade_municipios
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY r.nome_regiao
ORDER BY quantidade_municipios DESC;

-- 8. Qual é a população total estimada por estado?
-- Utilizando o ano de 2021 para fazer a soma correta sem duplicar anos.
SELECT 
    e.nome_uf, 
    SUM(p.valor) AS populacao_total_estimada
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
WHERE p.ano = 2021
GROUP BY e.nome_uf
ORDER BY populacao_total_estimada DESC;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT 
    e.nome_uf, 
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf
ORDER BY quantidade_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.

-- a) Criando a tabela de teste
CREATE TABLE tabela_teste (
    id_teste INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cargo TEXT
);

-- b) Inserção (INSERT)
INSERT INTO tabela_teste (nome, cargo) 
VALUES ('Vanessa Castro', 'Data Scientist Trainee');

-- c) Alteração (UPDATE)
UPDATE tabela_teste 
SET cargo = 'Junior Data Scientist' 
WHERE nome = 'Vanessa Castro';

-- d) Remoção (DELETE)
DELETE FROM tabela_teste 
WHERE nome = 'Vanessa Castro';

-- e) Apagando a tabela de teste (para manter o banco limpo no final)
DROP TABLE IF EXISTS tabela_teste;