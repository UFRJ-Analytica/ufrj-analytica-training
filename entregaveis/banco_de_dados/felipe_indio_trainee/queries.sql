-- 1. Quais regiões existem na base? 
SELECT DISTINCT nome_regiao FROM regioes r;

-- 2. Quais estados pertencem a uma região escolhida (Nordeste)?
SELECT r.nome_regiao, e.nome_uf FROM estados e
JOIN regioes r
ON e.id_regiao = r.id_regiao
WHERE r.nome_regiao = 'Nordeste';

--3. Quais municípios pertencem a uma UF escolhida (Rio de Janeiro)?
SELECT e.nome_uf, m.nome_municipio FROM municipios m 
JOIN estados e
ON e.id_uf  = m.id_uf
WHERE e.nome_uf = 'Rio de Janeiro';

--4. Qual é o estado e a região de cada município?
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao FROM municipios m 
JOIN estados e ON e.id_uf  = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao;

--5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor? 
SELECT m.nome_municipio, e.nome_uf, r.nome_regiao, pm.ano, pm.valor FROM populacao_municipal pm
JOIN municipios m ON m.id_municipio = pm.id_municipio
JOIN estados e ON e.id_uf  = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao;

--6. Quantos municípios existem por estado?
SELECT e.nome_uf, COUNT(m.nome_municipio) contagem_de_muncipios FROM municipios m 
JOIN estados e ON e.id_uf  = m.id_uf
GROUP BY e.nome_uf;

--7. Quantos municípios existem por região? 
SELECT  r.nome_regiao, COUNT(m.nome_municipio) contagem_de_muncipios FROM municipios m 
JOIN estados e ON e.id_uf  = m.id_uf
JOIN regioes r ON r.id_regiao = e.id_regiao
GROUP BY r.nome_regiao ;

--8. Qual é a população total estimada por estado? 
SELECT e.nome_uf, SUM(pm.valor) populacao FROM populacao_municipal pm  
JOIN municipios m ON m.id_municipio = pm.id_municipio
JOIN estados e ON e.id_uf  = m.id_uf
GROUP BY e.nome_uf;

--9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
SELECT e.nome_uf, COUNT(m.nome_municipio) contagem_de_muncipios FROM municipios m 
JOIN estados e ON e.id_uf  = m.id_uf
GROUP BY e.nome_uf
ORDER BY contagem_de_muncipios DESC
LIMIT 10;

--10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela
DROP TABLE IF EXISTS tabela_teste;

CREATE TABLE tabela_teste(
 id INTEGER PRIMARY KEY,
 nome TEXT NOT NULL,
 profissao TEXT NOT NULL,
 salario INTEGER NOT NULL
);

INSERT INTO tabela_teste (id, nome, profissao, salario)
VALUES (1, 'Roberta', 'Professor', 8000);

UPDATE tabela_teste
SET salario = 10000
WHERE id = 1;

DELETE FROM tabela_teste
WHERE id = 1;