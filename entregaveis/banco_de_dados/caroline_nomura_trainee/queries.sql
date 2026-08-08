-- 1. Quais regiões existem na base?
SELECT * 
FROM regioes;

-- 2. Quais estados pertencem a uma região escolhida (Sudeste)?
SELECT nome_uf, sigla_uf 
FROM estados 
WHERE id_regiao = 3;

-- 3. Quais municípios pertencem a uma UF escolhida (Rondônia)?
SELECT nome_municipio 
FROM municipios 
WHERE id_uf = ;

-- 4. Qual é o estado e a região de cada município?
SELECT 
    m.nome_municipio, 
    e.nome_uf, 
    r.nome_regiao
FROM municipios m
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT 
    m.nome_municipio, 
    e.sigla_uf, 
    r.nome_regiao, 
    p.ano, 
    p.valor AS populacao_estimada
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao;

-- 6. Quantos municípios existem por estado?
SELECT 
    e.nome_uf, 
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf
ORDER BY quantidade_municipios;

-- 7. Quantos municípios existem por região?
SELECT 
    r.nome_regiao, 
    COUNT(m.id_municipio) AS quantidade_municipios
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY r.nome_regiao
ORDER BY quantidade_municipios;

-- 8. Qual é a população total estimada por estado?
SELECT 
    e.nome_uf, 
    SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
WHERE p.ano = 2025
GROUP BY e.nome_uf
ORDER BY populacao_total;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT 
    e.nome_uf, 
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
GROUP BY e.nome_uf
ORDER BY quantidade_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
CREATE TABLE funcionarios (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100)
);
INSERT INTO funcionarios (id, nome) VALUES (1, 'Maria S.');
UPDATE funcionarios SET nome = 'Maria Silva' WHERE id = 1;
DELETE FROM funcionarios WHERE id = 1;
DROP TABLE funcionarios;
