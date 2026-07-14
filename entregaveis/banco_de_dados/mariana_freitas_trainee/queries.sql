--1. Quais regiões existem na base?
SELECT
    id_regiao,
    sigla_regiao,
    nome_regiao
FROM regioes;

--2. Quais estados pertencem à região Sudeste?
SELECT
    e.id_uf,
    e.sigla_uf,
    e.nome_uf
FROM estados e
JOIN regioes r
ON e.id_regiao = r.id_regiao
WHERE r.nome_regiao = 'Sudeste';

--3. Quais municípios pertencem ao estado de São Paulo?
SELECT
    m.id_municipio,
    m.nome_municipio
FROM municipios m
JOIN estados e
ON m.id_uf = e.id_uf
WHERE e.sigla_uf = 'SP';

--4. Qual é o estado e a região de cada município?
SELECT
    m.nome_municipio,
    e.nome_uf,
    r.nome_regiao
FROM municipios m
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN regioes r
    ON e.id_regiao = r.id_regiao
ORDER BY
    r.nome_regiao,
    e.nome_uf,
    m.nome_municipio;

--5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor? 
SELECT
    m.nome_municipio,
    e.sigla_uf,
    e.nome_uf,
    r.nome_regiao,
    p.ano,
    p.valor
FROM populacao_municipal p
JOIN municipios m
ON p.id_municipio = m.id_municipio
JOIN estados e
ON m.id_uf = e.id_uf
JOIN regioes r
ON e.id_regiao = r.id_regiao;

--6. Quantos municípios existem por estado? 
SELECT
    e.nome_uf,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados e
JOIN municipios m
ON e.id_uf = m.id_uf
GROUP BY e.nome_uf
ORDER BY quantidade_municipios DESC;

--7. Quantos municípios existem por região?
SELECT
    r.nome_regiao,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM regioes r
JOIN estados e
ON r.id_regiao = e.id_regiao
JOIN municipios m
ON e.id_uf = m.id_uf
GROUP BY r.nome_regiao
ORDER BY quantidade_municipios DESC;

--8. Qual é a população estimada por estado?
SELECT
    e.nome_uf,
    SUM(p.valor) AS populacao_total
FROM estados e
JOIN municipios m
    ON e.id_uf = m.id_uf
JOIN populacao_municipal p
    ON m.id_municipio = p.id_municipio
GROUP BY
    e.nome_uf
ORDER BY
    populacao_total DESC;

--9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)? 
SELECT
    e.nome_uf,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados e
JOIN municipios m
    ON e.id_uf = m.id_uf
GROUP BY
    e.nome_uf
ORDER BY
    quantidade_municipios DESC
LIMIT 10;

--10.  Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela. 
CREATE TABLE teste1(
    id INTEGER PRIMARY KEY,
    nome TEXT
);
INSERT INTO teste1
VALUES (1,'Mariana');

UPDATE teste
SET nome='Mariana Freitas'
WHERE id=1;

DELETE FROM teste
WHERE id=1;
