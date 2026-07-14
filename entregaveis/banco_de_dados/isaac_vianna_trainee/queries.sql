-- 1. Quais regiões existem na base?
SELECT id_regiao, sigla_regiao, nome_regiao
FROM regioes
ORDER BY nome_regiao;

-- 2. Quais estados pertencem a uma região escolhida?
SELECT e.id_uf, e.sigla_uf, e.nome_uf
FROM estados e
JOIN regioes r ON r.id_regiao = e.id_regiao
WHERE r.nome_regiao = 'Sudeste'
ORDER BY e.nome_uf;

-- 3. Quais municípios pertencem a uma UF escolhida?
SELECT m.id_municipio, m.nome_municipio
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
WHERE e.sigla_uf = 'RJ'
ORDER BY m.nome_municipio;

-- 4. Qual é o estado e a região de cada município?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao
FROM municipios m
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
ORDER BY m.nome_municipio;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    p.ano,
    p.valor AS populacao_estimada
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
ORDER BY p.valor DESC;

-- 6. Quantos municípios existem por estado?
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
LEFT JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC;

-- 7. Quantos municípios existem por região?
SELECT
    r.nome_regiao,
    COUNT(m.id_municipio) AS qtd_municipios
FROM regioes r
JOIN estados e ON e.id_regiao = r.id_regiao
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY qtd_municipios DESC;

-- 8. Qual é a população total estimada por estado?
SELECT
    e.sigla_uf,
    e.nome_uf,
    SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY populacao_total DESC;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT
    e.sigla_uf,
    e.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios
FROM estados e
JOIN municipios m ON m.id_uf = e.id_uf
GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
ORDER BY qtd_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
DROP TABLE IF EXISTS teste_operacoes;

CREATE TABLE teste_operacoes (
    id_teste   INTEGER PRIMARY KEY,
    observacao TEXT NOT NULL
);

INSERT INTO teste_operacoes (id_teste, observacao)
VALUES (1, 'Registro criado para validar INSERT');

UPDATE teste_operacoes
SET observacao = 'Registro atualizado para validar UPDATE'
WHERE id_teste = 1;

SELECT * FROM teste_operacoes;

DELETE FROM teste_operacoes
WHERE id_teste = 1;

SELECT COUNT(*) AS linhas_restantes FROM teste_operacoes;
