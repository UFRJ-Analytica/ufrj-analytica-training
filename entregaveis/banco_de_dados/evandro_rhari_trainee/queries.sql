-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.


-- ---- Testando os comandos ----

SELECT 
    municipios.nome_municipio,
    populacao_municipal.valor,
    populacao_municipal.ano
    FROM municipios 
        INNER JOIN populacao_municipal
            ON municipios.id_municipio = populacao_municipal.id_municipio
    LIMIT 30;

SELECT 
    municipios.nome_municipio,
    populacao_municipal.valor,
    populacao_municipal.ano
    FROM municipios 
        JOIN populacao_municipal
            ON municipios.id_municipio = populacao_municipal.id_municipio
    LIMIT 30;

SELECT 
    municipios.nome_municipio,
    populacao_municipal.valor,
    populacao_municipal.ano
    FROM municipios 
        NATURAL JOIN populacao_municipal
    LIMIT 30;

SELECT 
    municipios.nome_municipio,
    populacao_municipal.valor,
    populacao_municipal.ano
    FROM municipios 
        JOIN populacao_municipal
            USING (id_municipio)
    LIMIT 30;



SELECT 
    muni.nome_municipio Municipio,
    pop.valor População,
    pop.ano Ano
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
    LIMIT 30;



SELECT 
    muni.nome_municipio Municipio,
    pop.valor População,
    pop.ano Ano
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
    WHERE pop.valor > 1000000;


SELECT 
    muni.nome_municipio Municipio,
    pop.valor População,
    pop.ano Ano
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
    ORDER BY muni.nome_municipio, pop.valor
    LIMIT 30;


SELECT 
    est.nome_uf Estado, 
    avg(pop.valor) "População Média"
    FROM municipios muni
        JOIN populacao_municipal pop
            ON muni.id_municipio = pop.id_municipio
        JOIN estados est
            ON muni.id_uf = est.id_uf
    GROUP BY est.id_uf;

SELECT 
    est.nome_uf Estado, 
    avg(pop.valor) "População Média"
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
        NATURAL JOIN estados est
    GROUP BY est.id_uf;


SELECT 
    reg.nome_regiao Estado, 
    avg(pop.valor) "População Média"
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
        NATURAL JOIN estados est
        NATURAL JOIN regioes reg
    GROUP BY reg.id_regiao;


SELECT 
    est.nome_uf Estado, 
    avg(pop.valor) "População Média"
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
        NATURAL JOIN estados est
    GROUP BY est.id_uf
    HAVING avg(pop.valor) > 50000;


-- ---- Entregas ----

-- 1. Quais regiões existem na base?
SELECT DISTINCT
    nome_regiao Nome
    FROM regioes
    ORDER BY Nome;

-- 2. Quais estados pertencem a uma regiao escolhida (Norte)?
SELECT DISTINCT
    est.nome_uf Estado
    FROM estados est
    WHERE est.id_regiao = 1
    ORDER BY Estado;

-- 3. Quais municípios pertencem a uma UF escolhida (RO)?
SELECT DISTINCT
    muni.nome_municipio Municipio
    FROM municipios muni
    WHERE muni.id_uf = 11
    ORDER BY Municipio;

-- 4. Qual é o estado e a região de cada município?
SELECT DISTINCT
    muni.nome_municipio Municipio,
    est.nome_uf Estado,
    reg.nome_regiao Região
    FROM municipios muni
        NATURAL JOIN estados est
        NATURAL JOIN regioes reg
    ORDER BY Municipio;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT DISTINCT
    muni.nome_municipio Municipio,
    pop.valor População,
    est.nome_uf Estado,
    reg.nome_regiao Região,
    pop.ano
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
        NATURAL JOIN estados est
        NATURAL JOIN regioes reg
    ORDER BY Municipio;

-- 6. Quantos municípios existem por estado?
SELECT DISTINCT
    est.nome_uf Estado,
    count(DISTINCT muni.id_municipio) as Municipios
    FROM municipios muni
        NATURAL JOIN estados est
    GROUP BY est.id_uf
    ORDER BY Estado;

-- 7. Quantos municípios existem por região?
SELECT DISTINCT
    reg.nome_regiao Região,
    count(DISTINCT muni.id_municipio) as Municipios
    FROM municipios muni
        NATURAL JOIN estados est
        NATURAL JOIN regioes reg
    GROUP BY reg.id_regiao
    ORDER BY Região;

-- 8. Qual é a população total estimada por estado?
SELECT DISTINCT
    est.nome_uf Estado,
    sum(pop.valor) "População total"
    FROM populacao_municipal pop
        NATURAL JOIN municipios muni
        NATURAL JOIN estados est
    GROUP BY est.id_uf
    ORDER BY Estado;

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT DISTINCT
    est.nome_uf Estado,
    sum(pop.valor) "População total"
    FROM populacao_municipal pop
        NATURAL JOIN municipios muni
        NATURAL JOIN estados est
    GROUP BY Estado
    ORDER BY "População total" DESC
    LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
DROP TABLE IF EXISTS personagens;

CREATE TABLE personagens (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    idade INT
);

INSERT INTO personagens (nome, idade)
    VALUES ('Kumiko Oumae', 15);

INSERT INTO personagens (nome, idade)
    VALUES ('Hatsune Miku', 16);

SELECT * FROM personagens;

UPDATE personagens
    SET idade=16
    WHERE nome='Kumiko Oumae';

SELECT * FROM personagens;

UPDATE personagens
    SET idade=17,
        nome='Oumae Kumiko'
    WHERE id=1;

SELECT * FROM personagens;

UPDATE personagens
    SET idade=18
    WHERE idade=17;

SELECT * FROM personagens;

DELETE FROM personagens WHERE id=1;
SELECT * FROM personagens;