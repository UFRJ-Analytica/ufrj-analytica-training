-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.


-- 1. Quais são os municípios mais populosos da base?

SELECT
    municipios.nome_municipio,
    populacao_municipal.valor AS populacao

FROM populacao_municipal

INNER JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio

ORDER BY populacao DESC

LIMIT 10;

-- 3. Qual é a população total estimada por região?

SELECT
    regioes.nome_regiao,
    SUM(populacao_municipal.valor) AS populacao_total

FROM populacao_municipal

INNER JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio

INNER JOIN estados
    ON municipios.id_uf = estados.id_uf

INNER JOIN regioes
    ON estados.id_regiao = regioes.id_regiao

GROUP BY regioes.id_regiao

ORDER BY populacao_total DESC;

-- 5. Quais municípios possuem população acima da média nacional dos municípios?

SELECT
    municipios.nome_municipio,
    populacao_municipal.valor AS populacao

FROM populacao_municipal

INNER JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio

WHERE populacao_municipal.valor > (
    SELECT AVG(valor)
    FROM populacao_municipal
)

ORDER BY populacao DESC;


-- 7. Quantos municípios pequenos, médios e grandes existem por região?

SELECT
    regioes.nome_regiao,

    CASE
        WHEN populacao_municipal.valor < 20000 THEN 'Pequeno'
        WHEN populacao_municipal.valor < 100000 THEN 'Médio'
        ELSE 'Grande'
    END AS classificacao,

    COUNT(*) AS quantidade_municipios

FROM populacao_municipal

INNER JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio

INNER JOIN estados
    ON municipios.id_uf = estados.id_uf

INNER JOIN regioes
    ON estados.id_regiao = regioes.id_regiao

GROUP BY
    regioes.id_regiao,
    classificacao

ORDER BY
    regioes.id_regiao,
    classificacao;


    -- 9. Quais estados possuem maior concentração populacional em poucos municípios?

SELECT
    estados.nome_uf,
    MAX(populacao_municipal.valor) AS maior_populacao_municipal,
    SUM(populacao_municipal.valor) AS populacao_total,
    MAX(populacao_municipal.valor) * 1.0
        / SUM(populacao_municipal.valor) AS concentracao

FROM populacao_municipal

INNER JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio

INNER JOIN estados
    ON municipios.id_uf = estados.id_uf

GROUP BY estados.id_uf

ORDER BY concentracao DESC;