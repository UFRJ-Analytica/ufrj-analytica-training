-- 1.Quais são os municípios mais populosos da base?
SELECT m.nome_municipio, p.valor
FROM municipios m
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
ORDER BY p.valor DESC LIMIT 10;

-- 2.Qual é a população total estimada por região?
SELECT r.nome_regiao, SUM(p.valor) AS populacao_total
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
GROUP BY r.nome_regiao;

-- 3.Qual é a população média dos municípios por estado?
SELECT e.nome_uf, AVG(p.valor) AS populacao_media
FROM estados e
JOIN municipios m ON e.id_uf = m.id_uf
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
GROUP BY e.nome_uf;

-- 4.Quais municípios possuem população acima da média nacional?
SELECT m.nome_municipio, p.valor
FROM municipios m
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
WHERE p.valor > (SELECT AVG(valor) FROM populacao_municipal);

-- 5.Qual região concentra a maior população estimada?
SELECT r.nome_regiao, SUM(p.valor) AS total_populacao
FROM regioes r
JOIN estados e ON r.id_regiao = e.id_regiao
JOIN municipios m ON e.id_uf = m.id_uf
JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
GROUP BY r.nome_regiao
ORDER BY total_populacao DESC LIMIT 1;