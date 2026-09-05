-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.
PRAGMA foreign_keys = ON;

SELECT *
FROM estados;
SELECT *
FROM estados
WHERE id_regiao = 3;

SELECT
    estados.nome_uf,
    regioes.nome_regiao
FROM estados
JOIN regioes
    ON estados.id_regiao = regioes.id_regiao;

SELECT
    id_uf,
    COUNT(*) AS quantidade_municipios
FROM municipios
GROUP BY id_uf;

INSERT INTO regioes (
    id_regiao,
    sigla_regiao,
    nome_regiao
)
VALUES (
    99,
    'XX',
    'Região de Teste'
);

UPDATE regioes
SET nome_regiao = 'Região de Teste Atualizada'
WHERE id_regiao = 99;

DELETE FROM regioes
WHERE id_regiao = 99;