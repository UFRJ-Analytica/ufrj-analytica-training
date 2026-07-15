-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.
-- Quais regiões existem na base?
SELECT nome_regiao FROM regioes r ;

-- Quais estados pertencem a uma região escolhida?
SELECT
    e.nome_uf
FROM estados e
JOIN regioes r ON r.id_regiao = e.id_regiao
WHERE r.nome_regiao = 'Sudeste'
ORDER BY e.nome_uf;

-- Quais municípios pertencem a uma UF escolhida?
SELECT
    m.nome_municipio
FROM municipios m
JOIN estados e 
WHERE e.sigla_uf = 'RJ';

-- Qual é o estado e a região de cada município?
SELECT 
	 m.id_municipio,
    m.nome_municipio,
    e.sigla_uf,
    e.nome_uf,
    r.nome_regiao
FROM municipios m 
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON  r.id_regiao = e.id_regiao
ORDER BY m.nome_municipio;
	
-- Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    p.ano,
    p.valor AS populacao_estimada
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e    ON e.id_uf = m.id_uf
JOIN regioes r    ON r.id_regiao = e.id_regiao
ORDER BY p.valor DESC;
 
-- Quantos municípios existem por estado?
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC;

-- Quantos municípios existem por região?
SELECT
    r.nome_regiao,
    COUNT(m.id_municipio) AS qtd_municipios
FROM regioes r
JOIN estados e    ON e.id_regiao = r.id_regiao
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY qtd_municipios DESC;

-- Qual é a população total estimada por estado?
SELECT
    e.sigla_uf,
    e.nome_uf,
    p.ano,
    SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e    ON e.id_uf = m.id_uf
WHERE p.ano = 2025
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf, p.ano
ORDER BY populacao_total DESC;

-- Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC
LIMIT 10;

-- Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.

DROP TABLE IF EXISTS teste_crud;
 
CREATE TABLE teste_crud (
    id_teste  INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    status    TEXT NOT NULL DEFAULT 'ativo'
);
 
-- INSERT: cria tres registros.
INSERT INTO teste_crud (descricao, status) VALUES ('Registro de teste A', 'ativo');
INSERT INTO teste_crud (descricao, status) VALUES ('Registro de teste B', 'ativo');
INSERT INTO teste_crud (descricao, status) VALUES ('Registro de teste C', 'ativo');
 

SELECT * FROM teste_crud ORDER BY id_teste;
 
-- UPDATE: altera o registro 1.
UPDATE teste_crud
SET status    = 'inativo',
    descricao = 'Registro de teste A (editado)'
WHERE id_teste = 1;
 

SELECT * FROM teste_crud ORDER BY id_teste;
 
-- DELETE: remove o registro 3.
DELETE FROM teste_crud
WHERE id_teste = 3;
 
SELECT * FROM teste_crud ORDER BY id_teste;
 



