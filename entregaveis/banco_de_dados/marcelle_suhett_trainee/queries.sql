-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1. Quais regiões existem na base? 5
SELECT id_regiao, sigla_regiao, nome_regiao
FROM regioes
ORDER BY nome_regiao;

-- 2. Quais estados pertencem a uma região escolhida?
SELECT re.sigla_uf, re.nome_uf
FROM estados re
JOIN regioes rr ON rr.id_regiao = re.id_regiao
WHERE rr.nome_regiao = "Sul" -- Alterar para região escolhida
ORDER BY re.nome_uf;

-- 3. Quais municípios pertencem a uma UF escolhida? 
SELECT m.nome_municipio
FROM municipios m
JOIN estados re ON m.id_uf = re.id_uf
WHERE re.nome_uf = "Rio de Janeiro" -- Alterar para UF escolhida
ORDER BY m.nome_municipio;

-- 4. Qual é o estado e a região de cada município? 
SELECT m.nome_municipio, re.nome_uf, rr.nome_regiao
FROM municipios m
JOIN estados re ON re.id_uf = m.id_uf
JOIN regioes rr ON rr.id_regiao = re.id_regiao
ORDER BY rr.nome_regiao, re.nome_uf, m.nome_municipio;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor? 
SELECT m.nome_municipio, re.nome_uf, rr.nome_regiao, pm.ano, pm.valor
FROM populacao_municipal pm
JOIN municipios m ON pm.id_municipio = m.id_municipio
JOIN estados re ON m.id_uf = re.id_uf
JOIN regioes rr ON rr.id_regiao = re.id_regiao
ORDER BY pm.valor DESC;
 
-- 6. Quantos municípios existem por estado? 
SELECT re.sigla_uf, re.nome_uf, COUNT(m.id_municipio) AS qtd_municipios
FROM estados re
JOIN municipios m ON re.id_uf = m.id_uf
GROUP BY re.sigla_uf
ORDER BY qtd_municipios DESC;

-- 7. Quantos municípios existem por região? 
SELECT rr.sigla_regiao, rr.nome_regiao, COUNT(m.id_municipio) AS qtd_municipios
FROM regioes rr
JOIN estados re ON rr.id_regiao = re.id_regiao
LEFT JOIN municipios m ON re.id_uf = m.id_uf 
GROUP BY rr.sigla_regiao
ORDER BY qtd_municipios DESC;

-- 8. Qual é a população total estimada por estado? 
SELECT re.sigla_uf, re.nome_uf, SUM(pm.valor) AS qtd_pop
FROM estados re 
JOIN municipios m ON re.id_uf = m.id_uf
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
GROUP BY re.sigla_uf
ORDER BY qtd_pop DESC;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT re.sigla_uf, re.nome_uf, COUNT(m.id_municipio) AS qtd_municipios
FROM estados re
JOIN municipios m ON re.id_uf = m.id_uf
GROUP BY re.sigla_uf
ORDER BY qtd_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro 
nessa tabela. 
DROP TABLE IF EXISTS teste_tabela;

CREATE TABLE teste_tabela (
    id BIGINT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    idade INT NOT NULL
)

INSERT INTO teste_tabela (id, nome, idade)
VALUES (1, 'Marcelle', 19);
INSERT INTO teste_tabela (id, nome, idade)
VALUES (2, 'Samara', 23);

UPDATE teste_tabela
SET idade = 20
WHERE id = 1;

DELETE FROM teste_tabela
WHERE id = 2;