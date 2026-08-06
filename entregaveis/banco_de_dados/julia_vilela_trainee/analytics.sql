-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.
PRAGMA foreign_keys = ON;

-- Quais são os municípios mais populosos da base? (TOP 3)
SELECT 
	m.nome_municipio,
	p.valor
FROM municipios m 
JOIN populacao_municipal p
ON m.id_municipio = p.id_municipio
ORDER BY valor DESC
LIMIT 3;

-- Quais municípios possuem população acima da média nacional dos municípios?
SELECT
    m.nome_municipio,
    p.valor AS populacao_estimada,
    ROUND(
        p.valor - (SELECT AVG(valor) FROM populacao_municipal WHERE ano = 2025)
    , 1) AS diferenca_para_media
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
WHERE p.ano = 2025
  AND p.valor > (SELECT AVG(valor) FROM populacao_municipal WHERE ano = 2025)
ORDER BY p.valor DESC;

-- Quantos municípios pequenos, médios e grandes existem na base?
SELECT
    CASE
        WHEN p.valor <  20000  THEN '1 - Pequeno (< 20 mil)'
        WHEN p.valor < 100000  THEN '2 - Medio (20 mil a 100 mil)'
        ELSE                        '3 - Grande (100 mil ou mais)'
    END AS porte,
    COUNT(*) AS qtd_municipios
FROM populacao_municipal p
WHERE p.ano = 2025
GROUP BY porte
ORDER BY porte;
	
-- Qual região concentra a maior população estimada?
SELECT
	r.nome_regiao,
	SUM(p.valor) AS populacao_total,
	ROUND(
        100.0 * SUM(p.valor) /
        (SELECT SUM(valor) FROM populacao_municipal WHERE ano = 2025)
    , 2) AS percentual_do_brasil
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e ON e.id_uf = m.id_uf 
JOIN regioes r ON r.id_regiao = e.id_regiao 
WHERE p.ano = 2025
GROUP BY r.nome_regiao
ORDER BY populacao_total DESC
LIMIT 1;

-- Que padrões aparecem ao comparar municípios, estados e regiões?
/*o Nordeste tem mais municipios que o Sudeste, mas o Sudeste tem
o dobro de municipios grandes e a maior populacao. Ou seja,
quantidade de municipios nao acompanha populacao.*/
SELECT
    r.nome_regiao,
    COUNT(DISTINCT e.id_uf)  AS qtd_estados,
    COUNT(m.id_municipio)    AS qtd_municipios,
    SUM(p.valor)             AS populacao_total,
    ROUND(AVG(p.valor), 0)   AS populacao_media_municipio,
    MAX(p.valor)             AS maior_municipio,
    ROUND(
        100.0 * SUM(CASE WHEN p.valor >= 100000 THEN 1 ELSE 0 END) / COUNT(*)
    , 2) AS pct_municipios_grandes
FROM populacao_municipal p
JOIN municipios m ON m.id_municipio = p.id_municipio
JOIN estados e    ON e.id_uf = m.id_uf
JOIN regioes r    ON r.id_regiao = e.id_regiao
WHERE p.ano = 2025
GROUP BY r.id_regiao, r.nome_regiao
ORDER BY populacao_total DESC;

	

	