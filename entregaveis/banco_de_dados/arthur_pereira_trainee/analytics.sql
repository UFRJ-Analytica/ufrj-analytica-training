-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.


--1. Quais são os municípios mais populosos da base?
select nome_municipio, valor as populacao from municipios natural join populacao_municipal 
order by 2 desc;
-- o munícipio mais populoso é São Paulo, com quase 12 milhões de habitantes. Em seguida temos o Rio de Janeiro, com um pouco mais da metade do 1º e em terceiro lugar temos Brasília com apenas 3 milhões.


--2. Quais são os municípios mais populosos de uma UF escolhida?
select nome_municipio, valor as populacao from municipios natural join populacao_municipal natural join estados 
where sigla_uf="ES"
order by 2 desc
limit 5;
--Curiosamente, a capital de Espírito Santo é apenas o 4º município mais populoso, estando atrás de Serra (1º),Vila Velha (2º) e Cariacica (3º). Ao menos Vitória está à frente de Cachoeiro de Itapemirim (5º).


--4. Qual é a população média dos municípios por estado?
select nome_uf,round(avg(valor)) as populacao_media from municipios natural join populacao_municipal natural join estados 
group by nome_uf
order by 2 desc;
--Distrito Federal, de forma bem destoante, está em primeiro com 3 milhões de habitantes. Em seguida temos o Rio de Janeiro, que apesar de ter uma capital com 6 milhões de 
--habitantes (como visto antes) possui apenas uma média de  187 mil habitantes/município. E em terceiro temos São Paulo, com uma média de 70 mil habitantes/município.


--5. Quais municípios possuem população acima da média nacional dos municípios?
select nome_municipio, valor as populacao_media from municipios natural join populacao_municipal where valor > (select avg(valor) from populacao_municipal)
order by 2 desc;
-- São 902 munícipios que possuem população acima da média nacional dos municípios, com o 1º sendo São Paulo e o último sendo Amarante do Maranhão com 38.335 habitantes. Portanto dá pra deduzir que a média nacional seja de 38 mil.


--8. Qual região concentra a maior população estimada?
select nome_regiao, sum(valor) as populacao_total
from populacao_municipal natural join municipios natural join estados natural join regioes
group by nome_regiao
order by 2 desc;
--A região com maior população é o Sudeste, com 88 milhões de habitantes. Em seguida temos o Nordeste, com 57 milhões e em terceiro o Sul com 31 milhões. Norte e Centro-Oeste estão em último, com respectivamente 18 e 17 milhões.



