-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

-- Quais regiões existem na base
SELECT DISTINCT nome FROM regiao;

-- Quais estados pertencem a uma região escolhida?
SELECT nome FROM estado WHERE id_regiao = 1;

--Quais municípios pertencem a uma UF escolhida?
SELECT nome FROM municipio WHERE id_estado = 11;

--Qual é o estado e a região de cada município?
SELECT m.nome, e.nome, r.nome 
FROM municipio m 
JOIN estado e ON m.id_estado = e.id
JOIN regiao r ON e.id_regiao = r.id;

--Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
SELECT m.nome, e.nome, r.nome, relatorio.ano, relatorio.valor
FROM municipio m 
JOIN estado e ON m.id_estado = e.id
JOIN regiao r ON e.id_regiao = r.id 
JOIN relatorio_populacao relatorio ON m.id = relatorio.id_municipio;

--Quantos municípios existem por estado?
SELECT e.nome, COUNT(m.id) as qtd
FROM municipio m
JOIN estado e ON m.id_estado = e.id
GROUP BY e.nome;

--Quantos municípios existem por região?
SELECT r.nome, COUNT(m.id) as qtd
FROM municipio m
JOIN estado e ON m.id_estado = e.id
JOIN regiao r ON r.id = e.id_regiao
GROUP BY r.nome;

--Qual é a população total estimada por estado?
SELECT e.nome, SUM(p.valor)
FROM estado e
JOIN municipio m ON e.id = m.id_estado
JOIN relatorio_populacao p ON m.id = p.id_municipio
WHERE p.ano = (SELECT MAX(ano) FROM relatorio_populacao)
GROUP BY e.nome;

--Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT e.nome, COUNT(m.id) as qtd
FROM municipio m
JOIN estado e ON m.id_estado = e.id
GROUP BY e.nome
ORDER BY qtd DESC
LIMIT 10;

--Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela
CREATE TABLE alunos(
    id INTEGER PRIMARY KEY,
    nome TEXT
);

INSERT INTO alunos(id, nome)
VALUES(1, 'Luiz');

UPDATE alunos SET nome = 'Luiz Paulo' WHERE id = 1;

DELETE FROM alunos WHERE id = 1;