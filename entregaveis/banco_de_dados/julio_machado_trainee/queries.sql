-- 1. Quais regiões existem na base?
SELECT nome_regiao FROM regioes;

-- 2. Quais estados pertencem ao Sudeste?

SELECT nome_uf FROM estados
WHERE id_regiao = 3;

-- 3. Quais municípios pertencem ao Espírito Santo?

SELECT nome_municipio, nome_uf FROM municipios
INNER JOIN estados
	ON 	municipios.id_uf = estados.id_uf
WHERE municipios.id_uf = 32;

-- 4. Qual é o estado e a região de cada município?

SELECT nome_municipio, nome_uf, nome_regiao FROM municipios m
INNER JOIN estados e
	ON m.id_uf = e.id_uf
INNER JOIN regioes r
	ON r.id_regiao = e.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?

SELECT nome_municipio, valor, unidade, nome_uf, nome_regiao, ano
FROM municipios m
INNER JOIN estados e
	ON m.id_uf = e.id_uf 
INNER JOIN regioes r
	ON e.id_regiao = r.id_regiao 
INNER JOIN recenseamento r2 
	ON r2.id_municipio = m.id_municipio 
INNER JOIN censos c
	ON r2.id_censo = c.id_censo
ORDER BY valor DESC;

-- 6. Quantos municípios existem por estado?

SELECT 
	nome_uf,
	COUNT(id_municipio) AS total_municipios 
FROM municipios m
INNER JOIN estados e
	ON m.id_uf = e.id_uf
GROUP BY e.nome_uf
ORDER BY total_municipios DESC;


-- 7. Quantos municípios existem por região?

SELECT 
	nome_regiao,
	COUNT(id_municipio) AS total_municipios 
FROM municipios m
INNER JOIN estados e
	ON m.id_uf = e.id_uf
INNER JOIN regioes r
	ON e.id_regiao = r.id_regiao
GROUP BY r.nome_regiao
ORDER BY total_municipios DESC;


-- 8. Qual é a população total estimada por estado?

SELECT
	nome_uf,
	SUM(valor) as pop,
	unidade
FROM municipios m
INNER JOIN estados e
	ON m.id_uf = e.id_uf
INNER JOIN recenseamento r
	ON m.id_municipio = r.id_municipio
GROUP BY e.nome_uf
ORDER BY pop DESC;


-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?

SELECT 
	nome_uf,
	COUNT(id_municipio) AS total_municipios 
FROM municipios m
INNER JOIN estados e
	ON m.id_uf = e.id_uf
GROUP BY e.nome_uf
ORDER BY total_municipios DESC
LIMIT 10;

-- 10. Tabela de teste de inserção, alteração e remoção.
DROP TABLE IF EXISTS teste;

CREATE TABLE teste(
	id INTEGER PRIMARY KEY,
	desc VARCHAR(50)
);
INSERT INTO teste VALUES
(1, "teste"),
(2, "teste2");

UPDATE teste
SET desc = "mudado"
WHERE id = 1;

DELETE FROM teste
WHERE id % 2 = 1;