-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.
--Questão 1: Quais regiões existem na base?
SELECT nome_regiao
FROM regioes;
--Questão 2: Quais estados pertencem a uma região escolhida?
SELECT e.nome_uf
FROM regioes r INNER JOIN estados e ON r.id_regiao = e.id_regiao
WHERE r.nome_regiao = 'Centro-Oeste';
--Questão 3: Quais municípios pertencem a uma UF escolhida?
SELECT m.nome_municipio
FROM municipios m INNER JOIN estados e ON m.id_uf  = e.id_uf 
WHERE e.nome_uf  = 'Mato Grosso';
--Questão 4: Qual é o estado e a região de cada município?
SELECT m.nome_municipio,
	   e.nome_uf,
	   r.nome_regiao
FROM municipios m INNER JOIN estados e ON m.id_uf  = e.id_uf 
	INNER JOIN regioes r ON r.id_regiao = e.id_regiao ;
--Questão 5: Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT m.nome_municipio,
	   e.nome_uf,
	   r.nome_regiao,
	   pm.ano,
	   pm.valor 
FROM municipios m INNER JOIN estados e ON m.id_uf  = e.id_uf 
	INNER JOIN regioes r ON r.id_regiao = e.id_regiao 
	INNER JOIN populacao_municipal pm ON pm.id_municipio =m.id_municipio ;
--Questão 6: Quantos municípios existem por estado?
SELECT COUNT(m.id_municipio) as total_municipios,
	   e.nome_uf
FROM municipios m INNER JOIN estados e ON m.id_uf  = e.id_uf 
GROUP BY (e.id_uf);
--Questão 7: Quantos municípios existem por região?
SELECT COUNT(m.id_municipio) as total_municipios,
	   r.nome_regiao 
FROM municipios m INNER JOIN estados e ON m.id_uf  = e.id_uf 
	 INNER JOIN regioes r ON e.id_regiao = r.id_regiao
GROUP BY (r.id_regiao);
--Questão 8: Qual é a população total estimada por estado?
SELECT
	   e.nome_uf,
	   pm.ano,
	   SUM(pm.valor) 
FROM municipios m INNER JOIN estados e ON m.id_uf  = e.id_uf 
	INNER JOIN populacao_municipal pm ON pm.id_municipio =m.id_municipio 
	GROUP BY(e.id_uf);
--Questão 9: Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT e.nome_uf,
       COUNT(m.id_municipio) AS total_municipios
FROM estados e INNER JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY (e.id_uf)
ORDER BY (total_municipios) DESC
LIMIT 10;
--Questão 10: Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
--???? criando
DROP TABLE IF EXISTS melhor_estado;

CREATE TABLE IF NOT EXISTS  melhor_estado(
	id_estado INTEGER PRIMARY KEY,
	nome_estado TEXT
);
---Inserindo
INSERT INTO melhor_estado (id_estado, nome_estado)
SELECT e.id_uf, e.nome_uf
FROM estados e
INNER JOIN municipios m ON e.id_uf = m.id_uf 
GROUP BY e.id_uf, e.nome_uf
HAVING COUNT(m.id_municipio) = 645;

UPDATE melhor_estado 
	SET nome_estado = 'Rio de Janeiro'
WHERE nome_estado = 'São Paulo';

SELECT * FROM melhor_estado;

DELETE FROM melhor_estado where nome_estado = 'Rio de Janeiro';

DROP TABLE IF EXISTS melhor_estado;









