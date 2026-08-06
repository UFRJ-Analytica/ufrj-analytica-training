-- 1. Populando Regiões
INSERT INTO regioes (id_regiao, sigla_regiao, nome_regiao)
SELECT DISTINCT id_regiao, sigla_regiao, nome_regiao 
FROM raw_municipios_com_populacao;

-- 2. Populando indicadores
INSERT INTO indicadores (nome_indicador)
SELECT DISTINCT indicador 
FROM raw_municipios_com_populacao;

-- 3. Populando estados
INSERT INTO estados (id_uf, nome_uf, sigla_uf, id_regiao)
SELECT DISTINCT id_uf, nome_uf, sigla_uf, id_regiao 
FROM raw_municipios_com_populacao;

-- 4. Populando municipios
INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf 
FROM raw_municipios_com_populacao;

--5. Populando fato_indicador_municipal
INSERT INTO fato_indicador_municipal (id_municipio, id_indicador, ano, valor)
SELECT 
    r.id_municipio, 
    i.id_indicador, 
    r.ano, 
    r.valor
FROM raw_municipios_com_populacao r
JOIN indicadores i ON r.indicador = i.nome_indicador;