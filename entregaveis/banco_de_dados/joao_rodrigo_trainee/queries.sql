-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1. Quais regiões existem na base?

SELECT nome_regiao 
FROM regioes;

-- 2. Quais estados pertencem a uma região escolhida?!
-- Escolhendo a região Sudeste:

SELECT nome_uf 
FROM estados e 
INNER JOIN regioes r ON e.id_regiao = r.id_regiao 
WHERE r.nome_regiao = 'Sudeste';

-- 3. Quais municípios pertencem a uma UF escolhida?
-- Escolhendo o Rio de Janeiro:

SELECT nome_municipio
FROM municipios m 
INNER JOIN estados e ON m.id_uf = e.id_uf 
WHERE e.nome_uf = 'Rio de Janeiro';

-- 4. Qual é o estado e a região de cada município?

SELECT 
	m.nome_municipio, 
	e.nome_uf, 
	r.nome_regiao 
FROM municipios m
INNER JOIN estados e ON m.id_uf = e.id_uf 
INNER JOIN regioes r ON e.id_regiao = r.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?

SELECT 
	m.nome_municipio, 
	e.nome_uf, 
	r.nome_regiao, 
	pm.ano, 
	pm.valor AS "População estimada"
FROM municipios m
INNER JOIN estados e ON m.id_uf = e.id_uf 
INNER JOIN regioes r ON e.id_regiao = r.id_regiao 
INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio;

-- 6. Quantos municípios existem por estado?

SELECT 
	e.nome_uf, 
	COUNT(m.id_municipio) AS "Quantidade de municípios"
FROM estados e
INNER JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf;

-- 7. Quantos municípios existem por região?

SELECT 
	r.nome_regiao, 
	COUNT(m.id_municipio) AS "Quantidade de municípios"
FROM regioes r
INNER JOIN estados e ON r.id_regiao = e.id_regiao 
INNER JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY r.nome_regiao;

-- 8. Qual é a população total estimada por estado?

SELECT 
	e.nome_uf, 
	SUM(pm.valor) AS "População estimada por estado"
FROM estados e 
INNER JOIN municipios m ON e.id_uf = m.id_uf
INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
GROUP BY e.nome_uf;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?

SELECT 
	e.nome_uf, 
	COUNT(m.id_municipio) AS "Quantidade de municípios"
FROM estados e
INNER JOIN municipios m ON e.id_uf = m.id_uf 
GROUP BY e.nome_uf
ORDER BY COUNT(m.id_municipio) DESC 
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro
-- nessa tabela.

-- Query para fins de teste:
DROP TABLE IF EXISTS populacao_estadual;

-- Vou fazer uma tabela baseada no item 8, sobre a população de cada estado
CREATE TABLE populacao_estadual (
	id_uf INTEGER PRIMARY KEY,
	nome_uf TEXT NOT NULL,
	ano INTEGER NOT NULL,
	valor FLOAT NOT NULL,
	unidade TEXT NOT NULL,
	fonte TEXT NOT NULL
);

-- Populando a tabela baseada na query do item 8
INSERT INTO populacao_estadual (id_uf, nome_uf, ano, valor, unidade, fonte)
SELECT 
	e.id_uf,
	e.nome_uf,
	pm.ano,
	SUM(pm.valor),
	pm.unidade,
	pm.fonte
FROM estados e 
INNER JOIN municipios m ON e.id_uf = m.id_uf
INNER JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
GROUP BY e.id_uf, e.nome_uf, pm.ano, pm.unidade, pm.fonte;

-- Alterando a população do Rio de Janeiro 
UPDATE populacao_estadual
SET valor = valor + 10000
WHERE nome_uf = 'Rio de Janeiro';

-- Query para conferir a alteração:
SELECT valor FROM populacao_estadual pe WHERE pe.nome_uf = 'Rio de Janeiro';

-- Removendo a linha do Rio de Janeiro
DELETE FROM populacao_estadual 
WHERE nome_uf = 'Rio de Janeiro';