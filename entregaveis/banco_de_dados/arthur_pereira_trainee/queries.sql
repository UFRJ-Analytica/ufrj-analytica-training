-- queries.sql
-- Escreva aqui suas consultas SQL obrigatórias.
-- Inclua SELECT, JOIN, GROUP BY, INSERT, UPDATE e DELETE.

--1. Quais regiões existem na base?
select nome_regiao as regiao from regioes
order by regiao;   

--2. Quais estados pertencem a uma região escolhida?
select nome_uf as estados from estados join regioes on regioes.id_regiao=estados.id_regiao
where regioes.nome_regiao = 'Norte';

--3. Quais municípios pertencem a uma UF escolhida?
select nome_municipio as municipios from municipios join estados on municipios.id_uf=estados.id_uf
where nome_uf = 'Espírito Santo';

--4. Qual é o estado e a região de cada município?
select nome_municipio,nome_uf,nome_regiao 
from municipios join estados on municipios.id_uf=estados.id_uf join regioes on regioes.id_regiao=estados.id_regiao;

--5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?
select nome_municipio as municipio,nome_uf as UF,nome_regiao as regiao,ano,valor
from populacao_municipal natural join municipios natural join estados natural join regioes;

--6. Quantos municípios existem por estado?
select nome_uf, count(nome_municipio) as quantidade_de_municipios
from municipios natural join estados
group by nome_uf
order by 2 desc; 

--7. Quantos municípios existem por região?
select nome_regiao, count(nome_municipio) as quantidade_de_municipios
from municipios natural join estados natural join regioes
group by nome_regiao
order by 2 desc; 

--8. Qual é a população total estimada por estado?
select nome_uf, valor as populacao_total
from populacao_municipal natural join municipios natural join estados
group by nome_uf
order by 2 desc;

--9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?
select nome_uf, count(nome_municipio) as quantidade_de_municipios
from municipios natural join estados
group by nome_uf
order by 2 desc
limit 10;

--10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.
create table aliens_ben_10 (
id integer primary key autoincrement,
nome varchar(100));
insert into aliens_ben_10 (nome) values ('calafrio');
update aliens_ben_10 set nome = 'friagem' where id = 1;
delete from aliens_ben_10 where id = 1;
drop table aliens_ben_10;