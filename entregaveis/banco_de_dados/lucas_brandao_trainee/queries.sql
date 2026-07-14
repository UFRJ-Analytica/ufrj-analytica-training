-- 1.Quais regiões existem na base?
SELECT * FROM regioes;

-- 2.Quais estados pertencem a uma região escolhida? (Ex: Região 1 - Norte)
SELECT * FROM estados WHERE id_regiao = 1;

-- 3.Quais municípios pertencem a uma UF escolhida? (Ex: UF 11 - RO)
SELECT * FROM municipios WHERE id_uf = 11;

-- 4.Qual é o estado e a região de cada município?
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao;

-- 5.Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao, p.ano, p.valor
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio;

-- 6.Quantos municípios existem por estado?
SELECT e.nome_uf, COUNT(m.id_municipio) AS total_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf;

-- 7.Quantos municípios existem por região?
SELECT r.nome_regiao, COUNT(m.id_municipio) AS total_municipios
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY r.nome_regiao;

-- 8.Qual é a população total estimada por estado?
SELECT e.nome_uf, SUM(p.valor) AS populacao_total
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
GROUP BY e.nome_uf;

-- 9.Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT e.nome_uf, COUNT(m.id_municipio) AS total_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf
ORDER BY total_municipios DESC
LIMIT 10;

-- 10.Teste de CRUD
CREATE TABLE teste (id INTEGER PRIMARY KEY, nome TEXT);
INSERT INTO teste (nome) VALUES ('Exemplo');
UPDATE teste SET nome = 'Atualizado' WHERE id = 1;
DELETE FROM teste WHERE id = 1;
DROP TABLE teste;