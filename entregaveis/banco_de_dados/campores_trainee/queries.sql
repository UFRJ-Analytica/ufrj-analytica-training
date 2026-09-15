-- 1. Quais regiões existem na base?
SELECT nome_regiao
FROM regioes;

-- 2. Quais estados pertencem a uma região escolhida?

SELECT nome_uf
FROM estados
WHERE id_regiao = 3;

--3. quais municipios pertencem a uma uf escolhida
SELECT *
FROM municipios
WHERE  id_uf = 33;

--4 estado e região de cada municipio
SELECT nome_municipio,nome_uf,nome_regiao
FROM municipios
INNER JOIN estados
    ON municipios.id_uf = estados.id_uf 
INNER JOIN regioes
    ON estados.id_regiao = regioes.id_regiao;


--5 qual a população estimada dos municipios, mostrando municipio, uf, regia, ano e valor

SELECT
    municipios.nome_municipio,
    estados.nome_uf,
    regioes.nome_regiao,
    populacao_municipal.ano,
    populacao_municipal.valor

FROM populacao_municipal

INNER JOIN municipios
    ON populacao_municipal.id_municipio=municipios.id_municipio

INNER JOIN estados
    ON municipios.id_uf= estados.id_uf

INNER JOIN regioes
    ON estados.id_regiao  =regioes.id_regiao;

-- 6. Quantos municípios existem por estado?

SELECT
    estados.nome_uf,
    COUNT(*) AS quantidade_municipios

FROM municipios

INNER JOIN estados
    ON municipios.id_uf=estados.id_uf

GROUP BY estados.id_uf;

-- 7. Quantos municípios existem por região?

SELECT
    regioes.nome_regiao,
    COUNT(*) AS quantidade_municipios

FROM municipios

INNER JOIN estados
    ON municipios.id_uf=estados.id_uf

INNER JOIN regioes
    ON estados.id_regiao=regioes.id_regiao

GROUP BY regioes.id_regiao;

-- 8. Qual é a população total estimada por estado?

SELECT
    estados.nome_uf,
    SUM(populacao_municipal.valor) AS populacao_total

FROM populacao_municipal

INNER JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio

INNER JOIN estados
    ON municipios.id_uf=estados.id_uf

GROUP BY estados.id_uf;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?

SELECT
    estados.nome_uf,
    COUNT(*) AS quantidade_municipios

FROM municipios

INNER JOIN estados
    ON municipios.id_uf = estados.id_uf

GROUP BY estados.id_uf

ORDER BY quantidade_municipios DESC

LIMIT 10;

-- 10. Criar uma tabela de teste e registrar uma inserção,
-- uma alteração e uma remoção.

CREATE TABLE teste(
    id INTEGER PRIMARY KEY,
    nome TEXT
);

INSERT INTO teste (id, nome)
VALUES (12, 'batata');

UPDATE teste
SET nome = 'batata Atualizado'
WHERE id = 12;

DELETE FROM teste
WHERE id = 12;

