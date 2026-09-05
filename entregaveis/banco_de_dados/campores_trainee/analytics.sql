-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

SELECT
    estados.nome_uf,
    SUM(populacao_municipal.valor) AS populacao_total
FROM populacao_municipal
JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio
JOIN estados
    ON municipios.id_uf = estados.id_uf
GROUP BY estados.id_uf
ORDER BY populacao_total DESC;

SELECT
    municipios.nome_municipio,
    populacao_municipal.valor AS populacao
FROM populacao_municipal
JOIN municipios
    ON populacao_municipal.id_municipio = municipios.id_municipio
ORDER BY populacao DESC
LIMIT 10;