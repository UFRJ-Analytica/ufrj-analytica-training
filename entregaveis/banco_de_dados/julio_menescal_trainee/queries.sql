-- queries.sql

-- 1. Quais regiões existem na base?

SELECT
	id_regiao,
	sigla_regiao,
	nome_regiao
FROM regioes;

-- 2. Quais estados pertencem à região Sudeste?

SELECT
    id_uf,
    sigla_uf,
    nome_uf,
    id_regiao
FROM estados
WHERE id_regiao = 3;

-- 3. Quais municípios pertencem ao estado do Rio de Janeiro?

SELECT
    id_municipio,
    nome_municipio,
    id_uf
FROM municipios
WHERE id_uf = 33
ORDER BY nome_municipio;

-- 4. Qual é o estado e a região de cada município?

SELECT
    m.nome_municipio,
    e.nome_uf,
    r.nome_regiao
FROM municipios AS m
JOIN estados AS e
    ON m.id_uf = e.id_uf
JOIN regioes AS r
    ON e.id_regiao = r.id_regiao
ORDER BY m.nome_municipio;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    p.ano,
    p.valor
FROM populacao_municipal AS p
JOIN municipios AS m
    ON p.id_municipio = m.id_municipio
JOIN estados AS e
    ON m.id_uf = e.id_uf
JOIN regioes AS r
    ON e.id_regiao = r.id_regiao
ORDER BY p.valor DESC;

-- 6. Quantos municípios existem por estado?

SELECT
    e.nome_uf,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados AS e
JOIN municipios AS m
    ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.nome_uf
ORDER BY quantidade_municipios DESC;

-- 7. Quantos municípios existem por região?

SELECT
    r.nome_regiao,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM regioes AS r
JOIN estados AS e
    ON r.id_regiao = e.id_regiao
JOIN municipios AS m
    ON e.id_uf = m.id_uf
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY quantidade_municipios DESC;

-- 8. Qual é a população total estimada por estado?

SELECT
    e.nome_uf,
    SUM(p.valor) AS populacao_total_estimada
FROM estados AS e
JOIN municipios AS m
    ON e.id_uf = m.id_uf
JOIN populacao_municipal AS p
    ON m.id_municipio = p.id_municipio
GROUP BY e.id_uf, e.nome_uf
ORDER BY populacao_total_estimada DESC;

-- 9. Quais são os 10 estados com maior quantidade de municípios?

SELECT
    e.nome_uf,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados AS e
JOIN municipios AS m
    ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.nome_uf
ORDER BY quantidade_municipios DESC
LIMIT 10;

-- 10. Criar uma tabela de teste e realizar INSERT, UPDATE e DELETE.

DROP TABLE IF EXISTS teste_operacoes;

CREATE TABLE teste_operacoes (
    id INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL
);

INSERT INTO teste_operacoes (id, descricao)
VALUES (1, 'Registro inicial');

UPDATE teste_operacoes
SET descricao = 'Registro alterado'
WHERE id = 1;

DELETE FROM teste_operacoes
WHERE id = 1;