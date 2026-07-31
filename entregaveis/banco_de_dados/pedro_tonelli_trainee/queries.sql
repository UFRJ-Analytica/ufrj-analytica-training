-- queries.sql
-- Consultas de exploracao e validacao do banco normalizado.
-- Baseadas nas tabelas finais: regioes, estados, municipios,
-- indicadores, fato_indicador_municipal.

PRAGMA foreign_keys = ON;

-- 1. Quais regioes existem na base?
SELECT id_regiao, sigla_regiao, nome_regiao
FROM regioes
ORDER BY nome_regiao;


-- 2. Quais estados pertencem a uma regiao escolhida? (exemplo: Sudeste)
SELECT e.sigla_uf, e.nome_uf
FROM estados e
JOIN regioes r ON r.id_regiao = e.id_regiao
WHERE r.nome_regiao = 'Sudeste'
ORDER BY e.nome_uf;


-- 3. Quais municipios pertencem a uma UF escolhida? (exemplo: RJ)
SELECT m.id_municipio, m.nome_municipio
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
WHERE e.sigla_uf = 'RJ'
ORDER BY m.nome_municipio;


-- 4. Qual e o estado e a regiao de cada municipio?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    e.nome_uf,
    r.nome_regiao
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
ORDER BY r.nome_regiao, e.sigla_uf, m.nome_municipio;


-- 5. Qual e a populacao estimada dos municipios, mostrando municipio, UF,
--    regiao, ano e valor?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    f.ano,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
JOIN indicadores i ON i.id_indicador = f.id_indicador
WHERE i.codigo = 'populacao_residente_estimada'
ORDER BY r.nome_regiao, e.sigla_uf, m.nome_municipio;


-- 6. Quantos municipios existem por estado?
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
LEFT JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC;


-- 7. Quantos municipios existem por regiao?
SELECT
    r.nome_regiao,
    COUNT(m.id_municipio) AS qtd_municipios
FROM regioes r
JOIN estados e ON e.id_regiao = r.id_regiao
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY qtd_municipios DESC;


-- 8. Qual e a populacao total estimada por estado?
SELECT
    e.sigla_uf,
    e.nome_uf,
    SUM(f.valor) AS populacao_total_estimada
FROM fato_indicador_municipal f
JOIN municipios m ON m.id_municipio = f.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_total_estimada DESC;


-- 9. Quais estados possuem uma quantidade elevada de municipios (Top 10 Estados)?
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC
LIMIT 10;


-- 10. Crie uma tabela simples de teste e registre uma insercao, uma
--     alteracao e uma remocao de registro nessa tabela.
DROP TABLE IF EXISTS teste_operacoes;

CREATE TABLE teste_operacoes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao   TEXT NOT NULL,
    criado_em   TEXT DEFAULT (datetime('now'))
);

-- insercao
INSERT INTO teste_operacoes (descricao)
VALUES ('registro inicial de teste');

-- alteracao
UPDATE teste_operacoes
SET descricao = 'registro de teste atualizado'
WHERE id = 1;

-- remocao
DELETE FROM teste_operacoes
WHERE id = 1;

-- conferencia: a tabela deve ficar vazia apos o DELETE acima
SELECT * FROM teste_operacoes;
