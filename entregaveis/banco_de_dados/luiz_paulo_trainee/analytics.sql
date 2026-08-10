-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.

-- Pergunta 1: Quais são os municípios mais populosos?
SELECT  m.nome, e.sigla, p.valor
FROM relatorio_populacao p
JOIN municipio m ON p.id_municipio = m.id
JOIN estado e ON m.id_estado = e.id
WHERE p.ano = (SELECT MAX(ano) FROM relatorio_populacao)
ORDER BY p.valor DESC
LIMIT 10;

--Pergunta 2: Qual a população estimada por região?
SELECT r.nome, SUM(p.valor) as total
FROM relatorio_populacao p
JOIN municipio m ON p.id_municipio = m.id
JOIN estado e ON m.id_estado = e.id
JOIN regiao r ON e.id_regiao = r.id
WHERE p.ano = (SELECT MAX(ano) FROM relatorio_populacao)
GROUP BY r.nome
ORDER BY total DESC;

-- Pergunta 3: Quais municipios possuem população acima da média nacional dos municípios?
SELECT m.nome, e.sigla, p.valor
FROM relatorio_populacao p
JOIN municipio m ON p.id_municipio = m.id
JOIN estado e ON m.id_estado = e.id
WHERE p.ano = (SELECT MAX(ano) FROM relatorio_populacao)
  AND p.valor > (
      SELECT AVG(valor) 
      FROM relatorio_populacao 
      WHERE ano = (SELECT MAX(ano) FROM relatorio_populacao)
  )
ORDER BY p.valor DESC;

--Pergunta 4: Quantos município pequenos, médios e grandes existem na base? Sendo: 
--Pequeno: até 20.000 habitantes
--Médio: de 20.001 a 100.000 habitantes
--Grande: acima de 100.000 habitantes
SELECT 
    CASE 
        WHEN p.valor <= 20000 THEN 'Pequeno'
        WHEN p.valor BETWEEN 20001 AND 100000 THEN 'Médio'
        ELSE 'Grande'
    END AS porte_municipio,
    COUNT(*) AS quantidade_municipios
FROM relatorio_populacao p
WHERE p.ano = (SELECT MAX(ano) FROM relatorio_populacao)
GROUP BY porte_municipio
ORDER BY quantidade_municipios DESC;

-- Pergunta 5: Qual a população média dos municípios por estado?
SELECT e.nome, e.sigla, ROUND(AVG(p.valor), 0) as populacao_media_por_municipio
FROM relatorio_populacao p
JOIN municipio m ON p.id_municipio = m.id
JOIN estado e ON m.id_estado = e.id
WHERE p.ano = (SELECT MAX(ano) FROM relatorio_populacao)
GROUP BY e.nome, e.sigla
ORDER BY populacao_media_por_municipio DESC;