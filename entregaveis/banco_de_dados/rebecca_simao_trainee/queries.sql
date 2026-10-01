-- queries.sql
-- fazer perguntas ao banco.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.
-- Sao 10 perguntas

-- 1. Quais regiões existem na base?
SELECT * 
FROM regioes
ORDER BY id_regiao;


-- 2. Quais estados pertencem a uma região escolhida? (Sudeste)
SELECT estados.nome_uf  AS estados_sudeste
FROM estados
JOIN regioes ON estados.id_regiao = regioes.id_regiao
WHERE regioes.nome_regiao = 'Sudeste'
ORDER BY estados_sudeste;


-- 3. Quais municípios pertencem a uma UF escolhida? (RJ)
SELECT municipios.nome_municipio AS municipios_rio
FROM municipios
JOIN estados ON estados.id_uf =municipios.id_uf
WHERE estados.sigla_uf = 'RJ'
ORDER BY municipios_rio;


-- 4. Qual é o estado e a região de cada município?
SELECT
    muni.nome_municipio AS municipio,
    est.nome_uf AS estado,
    reg.nome_regiao AS regiao
FROM municipios muni
JOIN estados est ON muni.id_uf = est.id_uf
JOIN regioes reg ON est.id_regiao = reg.id_regiao
ORDER BY regiao, estado, municipio;


-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT
    muni.nome_municipio AS municipio,
    est.sigla_uf AS uf,
    reg.nome_regiao AS regiao,
    popu.ano,
    popu.valor
FROM populacao_municipal popu -- primeiro comeca consultar nela (na filha)
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
JOIN regioes reg ON est.id_regiao = reg.id_regiao
WHERE popu.indicador = 'populacao_residente_estimada' -- o filtro
ORDER BY popu.valor DESC;
-- se eu quisesse limitar aos 10 maiores por ex bastava por: LIMIT 10


-- 6. Quantos municípios existem por estado?
SELECT 
    est.nome_uf AS estado, 
    COUNT(muni.id_municipio) AS quantidade_municipios
FROM estados est
JOIN municipios muni ON est.id_uf = muni.id_uf
GROUP BY est.id_uf, est.nome_uf
ORDER BY quantidade_municipios DESC;


-- 7. Quantos municípios existem por região?
SELECT
    reg.nome_regiao AS regiao,
    COUNT(muni.id_municipio) AS quantidade_municipios
FROM regioes reg
JOIN estados est ON reg.id_regiao = est.id_regiao
JOIN municipios muni ON est.id_uf = muni.id_uf
GROUP BY reg.id_regiao, reg.nome_regiao
ORDER BY quantidade_municipios DESC;


-- 8. Qual é a população total estimada por estado?
SELECT
    est.nome_uf AS estado,
    popu.ano,
    SUM(popu.valor) AS populacao_total_estimada
FROM populacao_municipal popu
JOIN municipios muni ON popu.id_municipio = muni.id_municipio
JOIN estados est ON muni.id_uf = est.id_uf
WHERE popu.indicador = 'populacao_residente_estimada'
GROUP BY est.id_uf, est.nome_uf, popu.ano
ORDER BY populacao_total_estimada DESC;


-- 9. Quais estados possuem uma quantidade elevada de municípios?
SELECT
    est.nome_uf AS estado,
    COUNT(muni.id_municipio) AS quantidade_municipios
FROM estados est
JOIN municipios muni ON est.id_uf = muni.id_uf
GROUP BY est.id_uf, est.nome_uf
ORDER BY quantidade_municipios DESC
LIMIT 5;


-- 10. Crie uma tabela simples de teste e registre uma inserção, 
--  uma alteração e uma remoção de registro nessa tabela.
DROP TABLE IF EXISTS filmes_teste;

CREATE TABLE filmes_teste (
    id_filme INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    situacao TEXT NOT NULL,
    feedback TEXT
);

INSERT INTO filmes_teste (id_filme,titulo,situacao)
VALUES (1,'Nem que a Vaca Tussa','quero assistir!!');
SELECT *
FROM filmes_teste;

UPDATE filmes_teste
SET situacao = 'assistido!',feedback='altissima qualidade'
WHERE id_filme = 1;
SELECT *
FROM filmes_teste;

DELETE FROM filmes_teste
WHERE id_filme = 1;
SELECT *
FROM filmes_teste;