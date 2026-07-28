-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1. Quais regiões existem na base? 
SELECT nome_regiao
FROM regioes;

-- 2. Quais estados pertencem a uma região escolhida? 
SELECT e.nome_uf, r.nome_regiao 
FROM estados e 
JOIN regioes r 
ON e.id_regiao = r.id_regiao 
WHERE r.nome_regiao = 'Sudeste';

-- 3. Quais municípios pertencem a uma UF escolhida? 
SELECT e.nome_uf, m.nome_municipio 
FROM estados e 
JOIN municipios m 
ON e.id_uf = m.id_uf 
WHERE e.sigla_uf = 'RJ';

-- 4. Qual é o estado e a região de cada município? 
SELECT m.nome_municipio, e.sigla_uf, r.nome_regiao
FROM municipios m 
JOIN estados e
ON m.id_uf = e.id_uf 
JOIN regioes r 
ON r.id_regiao = e.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor? 
SELECT m.nome_municipio, e.sigla_uf, r.nome_regiao, valor, ano
FROM municipios m 
JOIN estados e
ON m.id_uf = e.id_uf 
JOIN regioes r 
ON r.id_regiao = e.id_regiao
JOIN fato_indicador_municipal fim 
ON fim.id_municipio = m.id_municipio;

-- 6. Quantos municípios existem por estado? 
SELECT e.sigla_uf , COUNT(m.id_uf) AS quantidade_municipios 
FROM estados e 
JOIN municipios m 
ON e.id_uf = m.id_uf
GROUP BY e.sigla_uf;

-- 7. Quantos municípios existem por região? 
SELECT r.nome_regiao, COUNT(m.id_uf) AS quantidade_municipios
FROM municipios m 
JOIN estados e
ON m.id_uf = e.id_uf 
JOIN regioes r 
ON r.id_regiao = e.id_regiao
JOIN fato_indicador_municipal fim 
ON fim.id_municipio = m.id_municipio
GROUP BY r.nome_regiao;

-- 8. Qual é a população total estimada por estado? 
SELECT e.sigla_uf, SUM(valor) AS populacao
FROM municipios m 
JOIN estados e
ON m.id_uf = e.id_uf 
JOIN fato_indicador_municipal fim 
ON fim.id_municipio = m.id_municipio
GROUP BY e.sigla_uf;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)? 
SELECT e.sigla_uf , COUNT(m.id_uf) AS quantidade_municipios 
FROM estados e 
JOIN municipios m 
ON e.id_uf = m.id_uf
GROUP BY e.sigla_uf
ORDER BY quantidade_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela. 
CREATE TABLE teste_treinamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL
);
INSERT INTO teste_treinamento (descricao) VALUES ('Testando insercao da liga');
UPDATE teste_treinamento SET descricao = 'Texto alterado com sucesso' WHERE id = 1;
DELETE FROM teste_treinamento WHERE id = 1;
DROP TABLE teste_treinamento;