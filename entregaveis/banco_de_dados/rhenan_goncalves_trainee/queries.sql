-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- Q1 TODAS AS REGIOES (INCLUINDO MOME, ID E SIGLA)
SELECT * 
FROM regiao;

-- Q2 ESTDOS PERTENCETES AO SUDESTE
SELECT nome_uf, sigla_uf 
FROM UF 
WHERE id_regiao = (SELECT id_regiao FROM regiao WHERE nome_regiao = 'Sudeste');

-- Q3 MUNICIPIOS DO RJ
SELECT nome_municipio 
FROM Municipios 
WHERE id_uf = (SELECT id_uf FROM UF WHERE sigla_uf = 'RJ');

-- Q4 ESTADO E REGIAO DE CADA MUNICIPIO
SELECT m.nome_municipio, u.sigla_uf, r.sigla_regiao 
FROM Municipios m 
LEFT OUTER JOIN UF u ON m.id_uf = u.id_uf 
LEFT OUTER JOIN regiao r ON u.id_regiao = r.id_regiao;

-- Q5 POP ESTIMADA DOS MUNICIPIOS
SELECT Ano, valor, tabela_da_q4.* 
FROM censo 
LEFT OUTER JOIN (
    SELECT m.nome_municipio, u.sigla_uf, r.sigla_regiao, m.id_Municipio 
    FROM Municipios m 
    LEFT OUTER JOIN UF u ON m.id_uf = u.id_uf 
    LEFT OUTER JOIN regiao r ON u.id_regiao = r.id_regiao
) AS tabela_da_q4 ON censo.id_municipio = tabela_da_q4.id_municipio;

-- Q6 QNTS MUNICIPIOS POR ESTADO
SELECT COUNT(id_municipio), nome_uf 
FROM Municipios 
INNER JOIN UF ON Municipios.id_uf = UF.id_uf 
GROUP BY Municipios.id_uf 
ORDER BY nome_uf;

-- Q7 QNTS MUNICIPIOS POR REGIAO
SELECT COUNT(id_municipio), nome_regiao 
FROM (
    SELECT m.id_municipio, r.nome_regiao, r.id_regiao 
    FROM Municipios m 
    LEFT OUTER JOIN UF u ON m.id_uf = u.id_uf 
    LEFT OUTER JOIN regiao r ON u.id_regiao = r.id_regiao
) AS tabela_da_q4 
GROUP BY id_regiao 
ORDER BY nome_regiao;

-- Q8 POPULACAO TOTAL POR ESTADO
SELECT Ano, SUM(valor), sigla_uf 
FROM censo 
LEFT OUTER JOIN (
    SELECT u.sigla_uf, u.id_uf, r.sigla_regiao, m.id_Municipio 
    FROM Municipios m 
    LEFT OUTER JOIN UF u ON m.id_uf = u.id_uf 
    LEFT OUTER JOIN regiao r ON u.id_regiao = r.id_regiao 
) AS tabela_da_q4 ON censo.id_municipio = tabela_da_q4.id_municipio 
GROUP BY id_uf;

-- Q9 TOP 10 POPS
SELECT Ano, SUM(valor), sigla_uf 
FROM censo 
LEFT OUTER JOIN (
    SELECT u.sigla_uf, u.id_uf, r.sigla_regiao, m.id_Municipio 
    FROM Municipios m 
    LEFT OUTER JOIN UF u ON m.id_uf = u.id_uf 
    LEFT OUTER JOIN regiao r ON u.id_regiao = r.id_regiao 
) AS tabela_da_q4 ON censo.id_municipio = tabela_da_q4.id_municipio 
GROUP BY id_uf 
ORDER BY SUM(valor) DESC 
LIMIT 10;

-- Q10
CREATE TABLE test (
    id INT PRIMARY KEY, 
    val CHAR(3)
);

INSERT INTO test (id, val) 
VALUES (2, 'HEY');

UPDATE test 
SET val = 'BYE' 
WHERE id = 2;

DELETE FROM test 
WHERE id = 2;
