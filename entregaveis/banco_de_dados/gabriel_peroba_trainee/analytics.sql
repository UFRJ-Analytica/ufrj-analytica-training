-- Q1
SELECT 
    m.nome_municipio, 
    e.sigla_uf, 
    p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
ORDER BY p.valor DESC
LIMIT 10;

-- Q2
SELECT 
    r.nome_regiao, 
    SUM(p.valor) AS populacao_total
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
JOIN regioes r ON e.id_regiao = r.id_regiao
GROUP BY r.nome_regiao
ORDER BY populacao_total DESC;

-- Q3
SELECT 
    e.sigla_uf, 
    ROUND(AVG(p.valor), 2) AS media_populacional
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
GROUP BY e.sigla_uf
ORDER BY media_populacional DESC;

-- Q4
SELECT 
    CASE 
        WHEN p.valor < 50000 THEN 'Pequeno'
        WHEN p.valor BETWEEN 50000 AND 500000 THEN 'Médio'
        ELSE 'Grande'
    END AS porte_municipio,
    COUNT(m.id_municipio) AS quantidade_municipios
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
GROUP BY porte_municipio
ORDER BY quantidade_municipios DESC;

-- Q5
SELECT 
    m.nome_municipio, 
    e.sigla_uf, 
    p.valor AS populacao
FROM populacao_municipal p
JOIN municipios m ON p.id_municipio = m.id_municipio
JOIN estados e ON m.id_uf = e.id_uf
WHERE p.valor > (SELECT AVG(valor) FROM populacao_municipal)
ORDER BY p.valor DESC;