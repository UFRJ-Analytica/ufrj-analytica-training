-- queries.sql
-- 1. Quais regiões existem na base?
SELECT DISTINCT nome_regiao
FROM regioes;

-- 2. Quais estados pertencem a uma região escolhida?
SELECT DISTINCT nome_uf
FROM estados INNER JOIN regioes
ON estados.id_regiao == regioes.id_regiao
WHERE nome_regiao = 'Sudeste';

--3. Quais municípios pertencem a uma UF escolhida?
SELECT DISTINCT nome_municipio
FROM municipios INNER JOIN estados
ON estados.id_uf == municipios.id_uf
WHERE nome_uf == 'Rio de Janeiro';

--4. Qual é o estado e a região de cada município?
SELECT DISTINCT nome_uf, nome_regiao, nome_municipio 
FROM municipios INNER JOIN estados
ON estados.id_uf == municipios.id_uf
INNER JOIN regioes
ON estados.id_regiao == regioes.id_regiao;

--5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor
SELECT nome_municipio, nome_uf, nome_regiao, ano, valor
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio) INNER JOIN estados
USING(id_uf) INNER JOIN regioes USING (id_regiao)
WHERE indicador == 'populacao_residente_estimada'
ORDER BY valor DESC;

-- 6. Quantos municípios existem por estado?
SELECT nome_uf, count(DISTINCT nome_municipio) AS 'total_municipios'
FROM municipios INNER JOIN estados
USING(id_uf) GROUP BY nome_uf
ORDER BY total_municipios DESC;

--7. Quantos municípios existem por região?
SELECT nome_regiao, count(DISTINCT nome_municipio) AS 'total_municipios'
FROM municipios INNER JOIN estados
USING(id_uf) INNER JOIN regioes
USING (id_regiao) GROUP BY nome_regiao
ORDER BY total_municipios DESC;

-- 8. Qual é a população total estimada por estado?
SELECT nome_uf, SUM(valor) AS 'populacao_total'
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio) INNER JOIN estados
USING(id_uf)
WHERE indicador == 'populacao_residente_estimada'
GROUP BY nome_uf
ORDER BY populacao_total DESC;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT nome_uf, count(DISTINCT nome_municipio) AS 'total_municipios'
FROM municipios INNER JOIN estados
USING(id_uf) GROUP BY nome_uf
ORDER BY total_municipios DESC LIMIT 10;

--10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
DROP TABLE IF EXISTS Populacao_estadual;
CREATE TABLE 'Populacao_estadual'(
nome_uf TEXT PRIMARY KEY,
populacao_total BIGINT NOT NULL
);

INSERT INTO populacao_estadual(
nome_uf,
populacao_total
)
SELECT nome_uf, SUM(valor) AS 'populacao_total'
FROM populacao_municipal INNER JOIN municipios
USING(id_municipio) INNER JOIN estados
USING(id_uf)
WHERE indicador == 'populacao_residente_estimada'
GROUP BY nome_uf
ORDER BY populacao_total DESC;

UPDATE populacao_estadual
SET nome_uf = nome_uf || ' (populoso)'
WHERE populacao_total >= 10000000;

DELETE FROM populacao_estadual
WHERE populacao_total < 10000000;

