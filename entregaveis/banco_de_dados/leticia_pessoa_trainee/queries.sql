-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1 Quais regiões existem na base?
SELECT id_regiao, nome_regiao
FROM regioes;

-- 2. Quais estados pertencem a uma regiao escolhida?
SELECT est. nome_uf, est.sigla_uf
FROM estados est
JOIN regioes reg ON est.id_regiao = reg.id_regiao
WHERE reg.nome_regiao = 'Nordeste';

-- 3. Quais municipios pertencem a uma UF escolhida
SELECT mun.nome_municipio, est.sigla_uf
FROM municipios mun
JOIN estados est ON mun.id_uf = est.id_uf
WHERE est.sigla_uf = 'MG';

-- 4. Qual é o estado e a região de cada municipio
SELECT 
    mun.nome_municipio,
    est.sigla_uf,
    reg.nome_regiao
FROM municipios mun
JOIN estados est ON mun.id_uf = est.id_uf
JOIN regioes reg ON est.id_regiao = reg.id_regiao;

-- 5. Qual é a população estimada dos municipios, mostrando municipio, UF, região, ano e valor?
SELECT 
    mun.nome_municipio,
    est.sigla_uf,
    reg.nome_regiao,
    pop.valor_populacao,
    pop.ano
FROM populacao pop
JOIN municipios mun ON pop.id_municipio = mun.id_municipio
JOIN estados est ON mun.id_uf = est.id_uf
JOIN regioes reg ON est.id_regiao = reg.id_regiao;

-- 6. Quantos municipios existem por estado?
SELECT
    est.sigla_uf,
    COUNT(mun.id_municipio) AS qtd_municipios
FROM estados est
JOIN municipios mun ON est.id_uf = mun.id_uf
GROUP BY est.id_uf, est.sigla_uf
ORDER BY qtd_municipios DESC;

-- 7. Quantos municípios existem por região?
SELECT
    reg.nome_regiao,
    COUNT(mun.id_municipio) AS qtd_municipios
FROM regioes reg
JOIN estados est ON reg.id_regiao = est.id_regiao
JOIN municipios mun ON est.id_uf = mun.id_uf
GROUP BY reg.id_regiao, reg.nome_regiao
ORDER BY qtd_municipios DESC;

-- 8. Qual é a população total estimada por estado
SELECT 
    est.sigla_uf,
    SUM(pop.valor_populacao) AS populacao_total_estado
FROM estados est
JOIN municipios mun ON est.id_uf = mun.id_uf
JOIN populacao pop ON mun.id_municipio = pop.id_municipio
GROUP BY est.id_uf, est.nome_uf, est.sigla_uf
ORDER BY populacao_total_estado DESC;

-- 9. Quais estados possuem uma quantidade elevada de municipios (top 10 estados)
SELECT 
    est.sigla_uf,
    COUNT (mun.id_municipio) AS qtd_municipios
FROM estados est
JOIN municipios mun ON est.id_uf = mun.id_uf
GROUP BY est.id_uf, est.sigla_uf
ORDER BY qtd_municipios DESC
LIMIT 10;

-- =====================================================================================
--  10. Crie uma tabela simples de teste e registre uma inserção, alteração e remoção.
-- =====================================================================================

-- A. Criandos tabela de teste
CREATE TABLE tabela_teste(
    id_teste INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_desenvolvedora TEXT NOT NULL,
    status_projeto TEXT NOT NULL
);

-- B. INSERT
INSERT INTO tabela_teste(nome_desenvolvedora, status_projeto)
VALUES('Leticia', 'Em andamento');

-- C. UPDATE: Alterar insert que acabou de ser feito
UPDATE tabela_teste
SET status_projeto = 'Concluido'
WHERE nome_desenvolvedora = 'Leticia';

-- D. DELETE
DELETE FROM tabela_teste
WHERE nome_desenvolvedora = 'Leticia';

-- E. Limpeza
DROP TABLE tabela_teste;