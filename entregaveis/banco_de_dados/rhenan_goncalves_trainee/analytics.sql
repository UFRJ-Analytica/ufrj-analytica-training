-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.
--1 municipios + populosos da base
SELECT
    nome_municipio,
    valor
FROM Municipios
LEFT JOIN censo
    ON censo.id_municipio = Municipios.id_municipio
ORDER BY valor DESC
LIMIT 10;

--sp ta grandao

--2 municipios + populosos do rj
SELECT
    nome_municipio,
    valor
FROM Municipios
LEFT JOIN censo
    ON censo.id_municipio = Municipios.id_municipio
LEFT JOIN UF
    ON UF.id_uf = Municipios.id_uf
WHERE sigla_uf = "RJ"
ORDER BY valor DESC
LIMIT 10;

-- são joaão de meriti mentioned :D

--3 pop media dos municipios por estado
SELECT
    sigla_uf,
    AVG(valor) med
FROM Municipios
LEFT JOIN censo
    ON censo.id_municipio = Municipios.id_municipio
LEFT JOIN UF
    ON UF.id_uf = Municipios.id_uf
GROUP BY sigla_uf
ORDER BY med DESC;

--dado q o df so tem um municipio fica enorme comaparado com os outros

--4 municipios com populacao acima da media nacional
SELECT
    nome_municipio,
    valor
FROM censo
INNER JOIN Municipios
    ON Municipios.id_municipio = censo.id_municipio
WHERE valor >= (
    SELECT AVG(valor)
    FROM censo
)
ORDER BY valor DESC;

--cerca de 900 acima de media de um total de 5600 indica uma distribuiçao pendendo pra esquerda. de fato, media de 37k e tem municipio com masis de milhao

--5 regiao com maior populacao estimada
SELECT
    SUM(valor),
    nome_regiao
FROM censo
NATURAL JOIN Municipios
NATURAL JOIN UF
NATURAL JOIN regiao
GROUP BY nome_regiao
ORDER BY SUM(valor) DESC;

--geral no sudeste, poucos no c.o.