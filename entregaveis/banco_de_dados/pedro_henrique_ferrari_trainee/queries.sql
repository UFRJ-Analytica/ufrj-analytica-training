-- 1. Quais regiões existem na base?
SELECT r.nome_regiao
FROM regioes r
;
-- 2. Quais estados pertencem a uma região escolhida?
SELECT e.nome_uf
FROM estados e
WHERE e.id_regiao = 2 -- Nordeste 
;
-- 3. Quais municípios pertencem a uma UF escolhida?
SELECT m.nome_municipio, e.nome_uf 
FROM municipios m 
JOIN estados e
	ON m.id_uf = e.id_uf
WHERE e.nome_uf = 'Rio de Janeiro'
;
-- 4. Qual é o estado e a região de cada município?
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao
FROM municipios m 
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao, pm.ano, pm.valor
FROM municipios m 
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
JOIN populacao_municipal pm on m.id_municipio = pm.id_municipio
;

-- 6. Quantos municípios existem por estado?
SELECT e.nome_uf, COUNT(m.id_municipio) as quantidade_de_municipios
FROM municipios m 
JOIN estados e ON m.id_uf = e.id_uf
GROUP BY e.id_uf
ORDER BY quantidade_de_municipios DESC;

-- 7. Quantos municípios existem por região?
SELECT COUNT(m.id_municipio) as quantidade_de_municipios, r.nome_regiao
FROM municipios m 
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao 
GROUP BY r.id_regiao 
ORDER BY quantidade_de_municipios DESC;

-- 8. Qual é a população total estimada por estado?
SELECT e.nome_uf, SUM(pm.valor)
FROM populacao_municipal pm 
JOIN municipios m ON pm.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf 
GROUP BY e.id_uf 
ORDER BY SUM(pm.valor) DESC;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT e.nome_uf, COUNT(m.id_municipio) as quantidade_de_municipios
FROM municipios m 
JOIN estados e ON m.id_uf = e.id_uf
GROUP BY e.id_uf
ORDER BY quantidade_de_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela. 

DROP TABLE IF EXISTS table_teste;

CREATE TABLE table_teste(
	cpf TEXT PRIMARY KEY,
	nome TEXT NOT NULL,
	idade INTEGER NOT NULL
);

INSERT INTO table_teste(cpf, nome, idade) 
VALUES('090090090', 'Pedro Henrique', 22);

INSERT INTO table_teste(cpf, nome, idade) 
VALUES('123456789', 'Harry Kane', 22);

SELECT *
FROM table_teste;

UPDATE table_teste
SET 
	nome = 'Pedro Henrique Ferrari',
	idade = 19
WHERE cpf = '090090090';

SELECT *
FROM table_teste;

DELETE FROM table_teste
WHERE cpf = '090090090';

SELECT *
FROM table_teste;