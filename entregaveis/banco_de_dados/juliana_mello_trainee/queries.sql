-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- 1. Quais regiões existem na base?
SELECT
    r.id_regiao,
    r.nome_regiao,
    r.sigla_regiao
FROM regioes r;

-- 2. Quais estados pertencem a uma região escolhida?
SELECT
    e.id_uf,
    e.sigla_uf,
    e.nome_uf
FROM estados e
INNER JOIN regioes r -- o que "permance" das tabelas comparadas, o que acontece com dados sem match
-- nesse caso, só vai aparecer o que tiver match perfeito
ON e.id_regiao = r.id_regiao -- regra de como tabelas serão conectadas, a ponte
-- mostra os estados com a mesma região indicada
-- olha id_regiao na tabela de estados (e) e na tabela de regiões (r) e cola as linhas com eles iguais lado a lado
WHERE r.nome_regiao = 'Nordeste';

-- 3. Quais municípios pertencem a uma UF escolhida?
SELECT
    m.nome_municipio
FROM municipios m
INNER JOIN estados e
ON m.id_uf = e.id_uf
WHERE e.nome_uf = 'Rio de Janeiro';

-- 4. Qual é o estado e a região de cada município?
SELECT -- o que quer impresso na tela
    m.id_municipio,
    m.nome_municipio,
    e.nome_uf,
    r.nome_regiao
FROM municipios m
INNER JOIN estados e 
ON m.id_uf = e.id_uf -- nao usa o nome ou sigla no ON pq usar texto pra ligar tabela é mais lento
INNER JOIN regioes r
ON e.id_regiao = r.id_regiao;

-- 5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT
    m.nome_municipio,
    p.valor,
    p.ano,
    e.nome_uf,
    r.nome_regiao
FROM municipios m -- bota no FROM a tabela que é o assunto principal
INNER JOIN populacao_municipal p
ON m.id_municipio = p.id_municipio
INNER JOIN estados e
ON m.id_uf = e.id_uf
INNER JOIN regioes r
ON e.id_regiao = r.id_regiao -- id do estado das tabelas municipios e estados iguais, ent ver a regiao

-- 6. Quantos municípios existem por estado?
SELECT
   -- m.nome_municipio,
    e.nome_uf,
    COUNT(m.id_municipio) as qntd_municipios -- conta a quantidade de id_municipio na tabela municipios e guarda como a variavel qntd_municipios
FROM estados e -- municipios por estado, ent estados é a tabela principal
INNER JOIN municipios m
ON m.id_uf = e.id_uf
GROUP BY e.nome_uf -- agrupa linhas com a mesma característica, transforma linhas repetidas em um único resumo
-- junta em um bloco todas as linhas que tem o mesmo nome_uf, ou seja, vai ficar um bloco por estado com sua quantidade de municipios
ORDER BY qntd_municipios DESC; 

-- 7. Quantos municípios existem por região?
SELECT
    r.nome_regiao,
COUNT(m.id_municipio) as qntd_municipios
FROM regioes r
INNER JOIN estados e
ON r.id_regiao = e.id_regiao -- como o municipio é conectado a estado, teem que ambém juntar pelo estado
INNER JOIN municipios m
ON m.id_uf = e.id_uf
GROUP BY r.nome_regiao
ORDER BY qntd_municipios DESC;

-- 8. Qual é a população total estimada por estado?
SELECT
    e.nome_uf,
    p.ano,
    SUM(p.valor) as pop_total
FROM estados e
INNER JOIN municipios m 
ON m.id_uf = e.id_uf
INNER JOIN populacao_municipal p
ON p.id_municipio = m.id_municipio
GROUP BY e.nome_uf, p.ano -- cria caixa única pra cda combinação estado + ano
ORDER BY e.nome_uf, p.ano; -- ordena por ordem alafabética do nome dos estados e ordem cronológica dos anos

-- 9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT 
    e.nome_uf,
    COUNT(m.id_municipio) as qntd_municipios
FROM estados e
INNER JOIN municipios m
ON m.id_uf = e.id_uf
GROUP BY e.nome_uf -- obs usa GROUP BY só quando quer resumir e juntar linha usando função matemática
ORDER BY qntd_municipios DESC
LIMIT 10;

-- 10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro
-- nessa tabela.

DROP TABLE IF EXISTS teste;

CREATE TABLE teste (
    id_teste INTEGER PRIMARY KEY AUTOINCREMENT, -- atualiza sozinho
    nome TEXT NOT NULL,
    estado TEXT NOT NULL
);

INSERT INTO teste -- insercções
    (nome, estado) -- não insere o valor de id_teste
    VALUES ('teste A', 'ativo');

INSERT INTO teste 
    (nome, estado)
    VALUES ('teste B', 'ativo');

INSERT INTO teste 
    (nome, estado)
    VALUES ('teste C', 'ativo');


SELECT * FROM teste -- "printa" a tabela
ORDER BY id_teste; 

UPDATE teste -- alteração
    SET nome = 'mudado',
        estado = 'inativo'
WHERE id_teste = 2;

DELETE FROM teste -- remoção
WHERE id_teste = 3;

SELECT * FROM teste -- "printa" a tabela
ORDER BY id_teste; 