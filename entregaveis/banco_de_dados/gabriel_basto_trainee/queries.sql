-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.
PRAGMA foreign_keys  = ON;

--1. Quais regiões existem na base?
SELECT
	id_regiao,
	sigla_regiao,
	nome_regiao
FROM regioes
ORDER BY nome_regiao;

--2. Quais estados pertencem a uma regiao escolhida?
SELECT 
	e.id_uf,
	e.sigla_uf,
	e.nome_uf
FROM estados e 
JOIN regioes r on r.id_regiao = e.id_regiao
WHERE r.sigla_regiao = 'CO'
ORDER BY e.nome_uf;

--3. Quais municípios pertencem a uma UF escolhida?
SELECT 
	m.id_municipio,
	m.nome_municipio
FROM municipios m 
JOIN estados e ON e.id_uf = m.id_uf
WHERE e.sigla_uf = 'RJ'
ORDER BY m.nome_municipio ;
--4. Qual é o estado e a região de cada município?
SELECT 
	m.nome_municipio,
	e.nome_uf,
	e.sigla_uf,
	r.nome_regiao
FROM municipios m 
JOIN estados e ON e.id_uf = m.id_uf 
JOIN regioes r ON r.id_regiao = e.id_regiao 
ORDER BY m.nome_municipio;
--5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor? 
SELECT 
	m.nome_municipio,
	e.sigla_uf,
	r.nome_regiao,
	f.ano,
	f.valor AS populacao_estimada
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio 
JOIN estados e ON e.id_uf  = m.id_uf 
JOIN regioes r ON r.id_regiao = e.id_regiao 
JOIN indicadores i ON i.id_indicador  = f.id_indicador 
WHERE i.nome_indicador  = 'populacao_residente_estimada'
ORDER BY m.nome_municipio ;
--6.Quantos municípios existem por estado?
SELECT 
	e.sigla_uf,
	e.nome_uf,
	COUNT(m.id_municipio) AS qtd_municipios
FROM estados e 
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf , e.sigla_uf , e.nome_uf 
ORDER BY qtd_municipios DESC;
--7.Quantos municípios existem por região?
SELECT 
	r.nome_regiao,
	COUNT(m.id_municipio) AS qtd_municpios
FROM regioes r 
JOIN estados e ON e.id_regiao = r.id_regiao 
JOIN municipios m  ON m.id_uf = e.id_uf 
GROUP BY r.id_regiao , r.nome_regiao 
ORDER BY qtd_municpios ;
--8.Qual é a população total estimada por estado?
SELECT
	e.sigla_uf,
	e.nome_uf,
	SUM(f.valor) AS populacao_total_estimada
FROM estados e
JOIN municipios m ON m.id_uf  = e.id_uf 
JOIN fato_indicador_municipal f ON f.id_municipio  = m.id_municipio  
JOIN indicadores i ON i.id_indicador  = f.id_indicador 
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf 
ORDER BY populacao_total_estimada DESC;

--9.Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT 
	e.sigla_uf,
	e.nome_uf,
	COUNT(m.id_municipio) AS qtd_municpios
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf 
GROUP BY e.id_uf , e.sigla_uf , e.nome_uf
ORDER BY qtd_municpios DESC
LIMIT 10;
--10.Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela. 
DROP TABLE IF EXISTS tab_teste;
CREATE TABLE tab_teste(
	id_teste INTEGER PRIMARY KEY AUTOINCREMENT,
	descricao TEXT NOT NULL,
	valor INTEGER
);

INSERT INTO tab_teste(descricao,valor)
VALUES('registro inicial', 20);

UPDATE tab_teste
SET valor = 40
WHERE descricao = 'registro inicial';

DELETE FROM tab_teste
WHERE descricao = 'registro inicial';

SELECT * FROM tab_teste;
