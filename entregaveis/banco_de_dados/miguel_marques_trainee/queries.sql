-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

PRAGMA foreign_keys = ON;


-- 1. Quais regiões existem na base?
SELECT
    id_regiao,
    sigla_regiao,
    nome_regiao
FROM regioes;



-- 2. Quais estados pertencem à região Sudeste?
SELECT
    e.nome_uf,
    e.sigla_uf
FROM estados e
JOIN regioes r
    ON e.id_regiao = r.id_regiao
WHERE r.nome_regiao = 'Sudeste';



-- 3. Quais municípios pertencem ao estado do Rio de Janeiro?
SELECT
    m.nome_municipio
FROM municipios m
JOIN estados e
    ON m.id_uf = e.id_uf
WHERE e.sigla_uf = 'RJ';



-- 4. Qual é o estado e a região de cada município?
SELECT
    m.nome_municipio,
    e.nome_uf,
    r.nome_regiao
FROM municipios m
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN regioes r
    ON e.id_regiao = r.id_regiao;



-- 5. Qual é a população estimada dos municípios?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    f.ano,
    f.valor
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN regioes r
    ON e.id_regiao = r.id_regiao
JOIN indicadores i
    ON f.id_indicador = i.id_indicador
WHERE i.nome_indicador = 'População';



-- 6. Quantos municípios existem por estado?
SELECT
    e.nome_uf,
    COUNT(*) AS quantidade_municipios
FROM municipios m
JOIN estados e
    ON m.id_uf = e.id_uf
GROUP BY e.nome_uf
ORDER BY quantidade_municipios DESC;



-- 7. Quantos municípios existem por região?
SELECT
    r.nome_regiao,
    COUNT(*) AS quantidade_municipios
FROM municipios m
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN regioes r
    ON e.id_regiao = r.id_regiao
GROUP BY r.nome_regiao
ORDER BY quantidade_municipios DESC;



-- 8. Qual é a população total estimada por estado?
SELECT
    e.nome_uf,
    SUM(f.valor) AS populacao_total
FROM fato_indicador_municipal f
JOIN municipios m
    ON f.id_municipio = m.id_municipio
JOIN estados e
    ON m.id_uf = e.id_uf
JOIN indicadores i
    ON f.id_indicador = i.id_indicador
WHERE i.nome_indicador = 'População'
GROUP BY e.nome_uf
ORDER BY populacao_total DESC;



-- 9. Quais estados possuem a maior quantidade de municípios? (Top 10)
SELECT
    e.nome_uf,
    COUNT(*) AS quantidade_municipios
FROM municipios m
JOIN estados e
    ON m.id_uf = e.id_uf
GROUP BY e.nome_uf
ORDER BY quantidade_municipios DESC
LIMIT 10;



-- 10. Criar tabela de teste com INSERT, UPDATE e DELETE

CREATE TABLE IF NOT EXISTS teste (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);


INSERT INTO teste (nome)
VALUES ('Registro teste');


UPDATE teste
SET nome = 'Registro atualizado'
WHERE id = 1;


DELETE FROM teste
WHERE id = 1;