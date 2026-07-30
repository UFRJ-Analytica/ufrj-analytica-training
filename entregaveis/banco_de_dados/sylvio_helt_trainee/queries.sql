PRAGMA foreign_keys = ON;

-- 1. Quais regiões existem na base?

SELECT
    id_regiao,
    sigla_regiao,
    nome_regiao
FROM regioes
ORDER BY nome_regiao;

-- 2. Quais estados pertencem a uma região escolhida?

SELECT
    e.id_uf,
    e.sigla_uf,
    e.nome_uf,
    r.nome_regiao
FROM estados AS e
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
WHERE r.nome_regiao = 'Nordeste'
ORDER BY e.nome_uf;

-- 3. Quais municípios pertencem a uma UF escolhida?

SELECT
    m.id_municipio,
    m.nome_municipio,
    e.sigla_uf
FROM municipios AS m
JOIN estados AS e
    ON e.id_uf = m.id_uf
WHERE e.sigla_uf = 'SE'
ORDER BY m.nome_municipio;

-- 4. Qual é o estado e a região de cada município?

SELECT
    m.id_municipio,
    m.nome_municipio,
    e.sigla_uf,
    e.nome_uf,
    r.nome_regiao
FROM municipios AS m
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
ORDER BY
    r.nome_regiao,
    e.nome_uf,
    m.nome_municipio;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    f.ano,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
ORDER BY
    f.ano DESC,
    f.valor DESC;

-- 6. Quantos municípios existem por estado?

SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados AS e
LEFT JOIN municipios AS m
    ON m.id_uf = e.id_uf
GROUP BY
    e.id_uf,
    e.sigla_uf,
    e.nome_uf
ORDER BY quantidade_municipios DESC;

-- 7. Quantos municípios existem por região?

SELECT
    r.nome_regiao,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM regioes AS r
LEFT JOIN estados AS e
    ON e.id_regiao = r.id_regiao
LEFT JOIN municipios AS m
    ON m.id_uf = e.id_uf
GROUP BY
    r.id_regiao,
    r.nome_regiao
ORDER BY quantidade_municipios DESC;

-- 8. Qual é a população total estimada por estado?

SELECT
    e.sigla_uf,
    e.nome_uf,
    SUM(f.valor) AS populacao_total_estimada
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY
    e.id_uf,
    e.sigla_uf,
    e.nome_uf
ORDER BY populacao_total_estimada DESC;

-- 9. Quais estados possuem uma quantidade elevada de municípios?

SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM estados AS e
JOIN municipios AS m
    ON m.id_uf = e.id_uf
GROUP BY
    e.id_uf,
    e.sigla_uf,
    e.nome_uf
ORDER BY quantidade_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.

DROP TABLE IF EXISTS questao_10;

CREATE TABLE questao_10 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    situacao TEXT NOT NULL
);

INSERT INTO questao_10 (
    nome,
    situacao
)
VALUES (
    'Registro de teste',
    'Pendente'
);

SELECT *
FROM questao_10;

UPDATE questao_10
SET situacao = 'Concluída'
WHERE id = 1;

SELECT *
FROM questao_10;

DELETE FROM questao_10
WHERE id = 1;

SELECT *
FROM questao_10;