-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1. Quais regiões existem na base?
SELECT nome_regiao
FROM regioes;

-- 2. Quais estados pertencem a uma região escolhida?
SELECT e.nome_uf
FROM estados e
JOIN regioes r 
ON e.id_regiao = r.id_regiao
WHERE r.nome_regiao = 'Sudeste';

-- 3. Quais municípios pertencem a uma UF escolhida?
SELECT m.nome_municipio
FROM municipios m
JOIN estados e
ON m.id_uf  = e.id_uf
WHERE e.sigla_uf = 'RJ';

-- 4. Qual é o estado e a região de cada município?
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao
FROM municipios m
JOIN estados e
ON m.id_uf  = e.id_uf
JOIN regioes r
ON e.id_regiao = r.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT localidade.nome_municipio, localidade.nome_uf, localidade.nome_regiao, f.ano, f.valor
FROM fato_indicador_municipal f
JOIN (
	SELECT m.nome_municipio, e.nome_uf, r.nome_regiao, m.id_municipio
	FROM municipios m
	JOIN estados e
	ON m.id_uf  = e.id_uf
	JOIN regioes r
	ON e.id_regiao = r.id_regiao
) AS localidade
ON f.id_municipio = localidade.id_municipio;

-- 6. Quantos municípios existem por estado?
SELECT e.nome_uf, COUNT(m.id_municipio) as num_municipios
FROM municipios m
JOIN estados e
ON m.id_uf = e.id_uf
GROUP BY e.id_uf
ORDER BY e.nome_uf;

-- 7. Quantos municípios existem por região?
SELECT r.nome_regiao, COUNT(m.id_municipio) as num_municipios
FROM municipios m
JOIN estados e
ON m.id_uf = e.id_uf
JOIN regioes r
ON e.id_regiao = r.id_regiao
GROUP BY r.id_regiao
ORDER BY r.nome_regiao;

-- 8. Qual é a população total estimada por estado?
SELECT e.nome_uf, SUM(f.valor) as populacao, f.ano
FROM fato_indicador_municipal f
JOIN municipios m
ON f.id_municipio = m.id_municipio
JOIN estados e
ON m.id_uf = e.id_uf
WHERE f.indicador = 'populacao_residente_estimada'
GROUP BY e.id_uf, f.ano
ORDER BY e.nome_uf;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT e.nome_uf, COUNT(m.id_municipio) as num_municipios
FROM municipios m
JOIN estados e
ON m.id_uf = e.id_uf
GROUP BY e.id_uf
ORDER BY num_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
DROP TABLE IF EXISTS teste_simples;

CREATE TABLE teste_simples (
id INTEGER PRIMARY KEY,
nome TEXT NOT NULL,
num_filhos INTEGER NOT NULL
);

INSERT INTO teste_simples(nome, num_filhos)
VALUES ('Jacinto Leite Aquino Rego', 324);

INSERT INTO teste_simples(nome, num_filhos)
VALUES ('Giuseppe Camolly da Silva', 2);

UPDATE teste_simples
SET num_filhos = 3
WHERE nome = 'Giuseppe Camolly da Silva';

DELETE FROM teste_simples
WHERE id = 1;