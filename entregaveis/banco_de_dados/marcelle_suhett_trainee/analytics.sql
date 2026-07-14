-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- 1. Quais são os municípios mais populosos da base? 

SELECT m.nome_municipio, pm.valor AS qtd_pop
FROM municipios m 
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
GROUP BY m.nome_municipio
ORDER BY qtd_pop DESC
LIMIT 5;

-- São Paulo (11.904.961), Rio de Janeiro(6.730.729) e Brasília(2.996.899)

-- 2. Quais são os municípios mais populosos de uma UF escolhida? 

SELECT re.nome_uf, m.nome_municipio, pm.valor AS qtd_pop
FROM estados re 
JOIN municipios m ON m.id_uf = re.id_uf
JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio
WHERE re.sigla_uf = :uf_escolhida -- Vai aparecer uma janela no DBeaver para digitar a UF
ORDER BY qtd_pop DESC
LIMIT 5;

-- No RJ, os municípios mais populosos são Rio de Janeiro, São Gonçalo e Duque de Caxias.

-- 3. Qual é a população total estimada por região? 

SELECT rr.nome_regiao, SUM(pm.valor) AS qtd_pop
FROM populacao_municipal pm
JOIN municipios m ON pm.id_municipio = m.id_municipio
JOIN estados re ON re.id_uf = m.id_uf
JOIN regioes rr ON rr.id_regiao = re.id_regiao
GROUP BY rr.id_regiao, rr.nome_regiao
ORDER BY qtd_pop DESC;

-- As populações estimadas de cada região é: Sudeste(88825643), Nordeste(57244485), Sul(31310809), Norte(18801282) e Centro Oeste(17232941).

-- 4. Qual é a população média dos municípios por estado? 

SELECT 
    re.sigla_uf, re.nome_uf,
    SUM(pm.valor),
    COUNT(*) AS qtd_municipios,
    ROUND(AVG(pm.valor), 0) AS populacao_media
FROM populacao_municipal pm
JOIN municipios m ON pm.id_municipio = m.id_municipio
JOIN estados re ON m.id_uf = re.id_uf
GROUP BY re.id_uf, re.sigla_uf, re.nome_uf
ORDER BY populacao_media DESC;

-- O estado com maior média é o Distrito Federal mas ele só tem um município. Os próximos com maiores médias são Rio de Janeiro, São Paulo, Amazonas e Pará.

-- 5. Quais municípios possuem população acima da média nacional dos municípios? 

SELECT COUNT(m.id_municipio)
FROM municipios m -- Quantidade de municípios: 5570

SELECT SUM(pm.valor)
FROM populacao_municipal pm -- Quantidade total de habitantes: 213415160

-- Média nacional de habitantes por município: 213415160/5570 = 38.315

SELECT m.nome_municipio, e.sigla_uf, pm.valor 
FROM populacao_municipal pm
JOIN municipios m ON m.id_municipio = pm.id_municipio
JOIN estados    e ON e.id_uf        = m.id_uf
WHERE pm.valor > 38315
ORDER BY pm.valor DESC;

-- 902 munícipios de 5570 têm população maior que a média nacional de habitantes.

-- 8. Qual região concentra a maior população estimada? 

SELECT rr.nome_regiao, SUM(pm.valor) AS qtd_pop
FROM populacao_municipal pm
JOIN municipios m ON pm.id_municipio = m.id_municipio
JOIN estados re ON re.id_uf = m.id_uf
JOIN regioes rr ON rr.id_regiao = re.id_regiao
GROUP BY rr.id_regiao, rr.nome_regiao
ORDER BY qtd_pop DESC
LIMIT 1;

-- A região Sudeste concentra maior população.

-- 9. Quais estados possuem maior concentração populacional em poucos municípios? 

SELECT 
    re.sigla_uf, re.nome_uf,
    COUNT(m.id_municipio) AS qtd_municipios,
    SUM(pm.valor) AS qtd_pop
FROM populacao_municipal pm
JOIN municipios m ON pm.id_municipio = m.id_municipio
JOIN estados re ON re.id_uf = m.id_uf
GROUP BY re.sigla_uf, re.nome_uf
HAVING COUNT(m.id_municipio) < 60 
ORDER BY qtd_pop DESC;

-- É exibida uma lista de forma decrescente (DESC) pela quantidade total de população. Ou seja, o estado com menos de 60 municípios que tiver mais habitantes aparecerá no topo da lista. Nesse caso, temos o Distrito Federal, com 1 município e 2.996.899 habitantes.