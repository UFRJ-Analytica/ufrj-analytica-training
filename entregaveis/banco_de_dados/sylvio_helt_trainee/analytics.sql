-- 1. Quais são os municípios mais populosos da base?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
ORDER BY f.valor DESC
LIMIT 10;

-- 2. Quais são os municípios mais populosos de uma UF escolhida?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
  AND e.sigla_uf = 'SC'
ORDER BY f.valor DESC
LIMIT 10;

-- 3. Qual é a população total estimada por região?

SELECT
    r.nome_regiao,
    SUM(f.valor) AS populacao_total_estimada
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY
    r.id_regiao,
    r.nome_regiao
ORDER BY populacao_total_estimada DESC;

-- 4. Qual é a população média dos municípios por estado?

SELECT
    e.sigla_uf,
    e.nome_uf,
    ROUND(AVG(f.valor), 2) AS populacao_media_municipios
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY
    e.id_uf,
    e.sigla_uf,
    e.nome_uf
ORDER BY populacao_media_municipios DESC;

-- 5. Quais municípios possuem população acima da média nacional dos municípios?

SELECT
    m.nome_municipio,
    e.sigla_uf,
    r.nome_regiao,
    f.valor AS populacao_estimada
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
  AND f.valor > (
      SELECT AVG(f2.valor)
      FROM fato_indicador_municipal AS f2
      JOIN indicadores AS i2
          ON i2.id_indicador = f2.id_indicador
      WHERE i2.nome_indicador = 'populacao_residente_estimada'
  )
ORDER BY f.valor DESC;

-- 6. Quantos municípios pequenos, médios e grandes existem na base?
-- Pequeno: até 100.000 habitantes
-- Médio: de 100.000 até 750.000 habitantes
-- Grande: mais de 750.000 habitantes

SELECT
    CASE
        WHEN f.valor < 100000 THEN 'Pequeno'
        WHEN f.valor <= 750000 THEN 'Médio'
        ELSE 'Grande'
    END AS porte_municipio,
    COUNT(*) AS quantidade_municipios
FROM fato_indicador_municipal AS f
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY
	porte_municipio
ORDER BY
    CASE porte_municipio
        WHEN 'Pequeno' THEN 1
        WHEN 'Médio' THEN 2
        WHEN 'Grande' THEN 3
    END;

-- 7. Quantos municípios pequenos, médios e grandes existem por região?

SELECT
    r.nome_regiao,
    CASE
        WHEN f.valor < 100000 THEN 'Pequeno'
        WHEN f.valor <= 750000 THEN 'Médio'
        ELSE 'Grande'
    END AS porte_municipio,
    COUNT(*) AS quantidade_municipios
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY
    r.id_regiao,
    r.nome_regiao,
    porte_municipio 
ORDER BY
    r.nome_regiao,
    CASE porte_municipio
        WHEN 'Pequeno' THEN 1
        WHEN 'Médio' THEN 2
        WHEN 'Grande' THEN 3
    END;

-- 8. Qual região concentra a maior população estimada?

SELECT
    r.nome_regiao,
    SUM(f.valor) AS populacao_total_estimada
FROM fato_indicador_municipal AS f
JOIN municipios AS m
    ON m.id_municipio = f.id_municipio
JOIN estados AS e
    ON e.id_uf = m.id_uf
JOIN regioes AS r
    ON r.id_regiao = e.id_regiao
JOIN indicadores AS i
    ON i.id_indicador = f.id_indicador
WHERE i.nome_indicador = 'populacao_residente_estimada'
GROUP BY
    r.id_regiao,
    r.nome_regiao
ORDER BY populacao_total_estimada DESC
LIMIT 1;