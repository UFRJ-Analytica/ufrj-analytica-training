-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- 1.) Municípios mais populosos do Brasil
select m.nome_municipio, p.valor from municipio m
inner join populacao_municipal p on m.id_municipio = p.id_municipio
order by p.valor desc limit 10;

-- 2.) Municípios mais populosos do estado do Rio de Janeiro
select m.nome_municipio, p.valor from municipio m
inner join populacao_municipal p on m.id_municipio = p.id_municipio
inner join estado e on e.id_uf=m.id_estado
where e.nome_uf="Rio de Janeiro"
order by p.valor desc limit 10;

-- 3.) População média dos municípios agrupados por estado
select e.nome_uf, avg(p.valor) as media from municipio m
inner join populacao_municipal p on m.id_municipio = p.id_municipio
inner join estado e on e.id_uf=m.id_estado
group by e.nome_uf;


-- 4.) Municípios com população maior que a população média dos municípios
select m.nome_municipio, p.valor from municipio m
inner join populacao_municipal p
inner join (select avg(pm.valor) as media from populacao_municipal pm) as media_nacao
where p.valor>media_nacao.media;

-- 5.) Regiões reankeadas por população total
select r.nome_regiao, sum(p.valor) as total from populacao_municipal p
inner join municipio m on p.id_municipio = m.id_municipio
inner join estado e on m.id_estado=e.id_uf
inner join regiao r on r.id_regiao=e.id_regiao
group by nome_regiao
order by total desc;