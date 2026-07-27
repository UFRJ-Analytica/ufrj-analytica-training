-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.
-- 1.) Quais regioes existem na base?
select nome_regiao from regiao;

-- 2.) Quais estados pertencem a regiao norte?
select e.nome_uf from estado e
inner join regiao r on r.id_regiao=e.id_regiao
where r.nome_regiao='Norte';

-- 3.) Quais municípios pertencem ao estado do Rio de Janeiro?
select m.nome_municipio from municipio m
inner join estado e on m.id_estado=e.id_uf
where e.nome_uf='Rio de Janeiro';

-- 4.) Qual é o estado e a região de cada município?
select m.nome_municipio, e.nome_uf, r.nome_regiao
from municipio m inner join estado e on m.id_estado=e.id_uf
inner join regiao r on e.id_regiao=r.id_regiao;

-- 5.) Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
select m.nome_municipio, e.nome_uf, r.nome_regiao, c.ano, p.valor
from municipio m inner join estado e on m.id_estado=e.id_uf
inner join regiao r on e.id_regiao=r.id_regiao
inner join populacao_municipal p on m.id_municipio = p.id_municipio
inner join censo c on p.id_censo = c.id_censo;

-- 6.) Quantos municípios existem por estado?
select e.nome_uf, count(m.nome_municipio) as total from municipio m
inner join estado e on m.id_estado=e.id_uf
group by e.nome_uf;

-- 7.) Quantos municípios existem por região?
select r.nome_regiao, count(m.nome_municipio) as total from municipio m
inner join estado e on m.id_estado=e.id_uf
inner join regiao r on r.id_regiao=e.id_regiao
group by r.nome_regiao;

-- 8.) Qual é a população total estimada por estado?
select e.nome_uf, sum(p.valor) as total from populacao_municipal p
inner join municipio m on p.id_municipio=m.id_municipio
inner join estado e on m.id_estado=e.id_uf
group by e.nome_uf;

-- 9.) Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
select e.nome_uf, count(m.nome_municipio) as total from municipio m
inner join estado e on m.id_estado=e.id_uf
group by e.nome_uf
order by total desc limit 10;

-- 10.) Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
-- 10.1) Criação:
CREATE TABLE estado_mais_populoso(
	id_estado INTEGER PRIMARY KEY,
	nome_uf TEXT NOT NULL,
	populacao INTEGER NOT NULL,
	FOREIGN KEY (id_estado) REFERENCES estado(id_uf)
);
-- 10.2) Inserção:
INSERT INTO estado_mais_populoso(
	id_estado,
	nome_uf,
	populacao
)
select e.id_uf, e.nome_uf, sum(p.valor) as total from populacao_municipal p
inner join municipio m on p.id_municipio=m.id_municipio
inner join estado e on m.id_estado=e.id_uf
group by e.nome_uf order by total desc limit 1;
-- 10.3) Alteração:
UPDATE estado_mais_populoso SET populacao=46081000;
-- 10.4) Remoção:
DELETE FROM estado_mais_populoso WHERE id_estado=35;
