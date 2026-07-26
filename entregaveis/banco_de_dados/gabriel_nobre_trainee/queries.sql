-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- Perguntas Obrigatórias


-- 1. Quais regiões existem na base?
SELECT nome_regiao FROM regioes;

-- 2. Quais estados pertencem a uma região(Nordeste) escolhida?
SELECT e.nome_uf
FROM estados e
JOIN regioes r ON e.id_regiao = r.id_regiao
WHERE r.nome_regiao LIKE 'nordeste';

-- 3. Quais municípios pertencem a uma UF escolhida?

SELECT m.nome_municipio
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
WHERE e.nome_uf LIKE 'rio de janeiro';

-- 4. Qual é o estado e a região de cada município?

SELECT 
	m.nome_municipio,
	e.nome_uf,
	r.nome_regiao
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor? 

SELECT 
	m.nome_municipio,
	e.nome_uf,
	r.nome_regiao,
	f.ano,
	f.valor
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
JOIN fato_indicador_municipal f ON m.id_municipio = f.id_municipio;

-- 6. Quantos municípios existem por estado?
SELECT
	e.nome_uf,
	COUNT(m.id_municipio) AS total_municipios	
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf
ORDER BY total_municipios DESC;

-- 7. Quantos municípios existem por região? 
SELECT
	r.nome_regiao,
	COUNT(m.id_municipio) AS total_municipios	
FROM regioes r
JOIN estados e ON e.id_regiao = r.id_regiao
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY r.nome_regiao;

-- 8. Qual é a população total estimada por estado?

SELECT
	e.nome_uf,
	SUM(f.valor) AS populacao_total
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
GROUP BY e.nome_uf
ORDER BY populacao_total DESC;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?

SELECT
	e.nome_uf,
	SUM(f.valor) AS populacao_total
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf
JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
GROUP BY e.nome_uf
ORDER BY populacao_total DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela. 

CREATE TABLE teste (
id INTEGER PRIMARY KEY,
nome TEXT NOT NULL,
valor INT NOT NULL
);

INSERT INTO teste (id, nome, valor)
	VALUES(1, 'Exemplo', 100);

UPDATE teste
SET valor = 200
WHERE id = 1;

DELETE FROM teste
WHERE id = 1;

