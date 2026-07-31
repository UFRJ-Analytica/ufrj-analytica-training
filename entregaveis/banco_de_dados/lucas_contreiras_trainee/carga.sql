-- carga.sql
-- Carga das tabelas normalizadas a partir da tabela raw_municipios_com_populacao.

INSERT INTO regioes (id_regiao, sigla_regiao, nome_regiao)
SELECT DISTINCT id_regiao, sigla_regiao, nome_regiao
FROM raw_municipios_com_populacao
ORDER BY id_regiao;

INSERT INTO indicadores (nome_indicador)
SELECT DISTINCT indicador
FROM raw_municipios_com_populacao
ORDER BY indicador;

INSERT INTO estados (id_uf, nome_uf, sigla_uf, id_regiao)
SELECT DISTINCT id_uf, nome_uf, sigla_uf, id_regiao
FROM raw_municipios_com_populacao
ORDER BY id_uf;

INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios_com_populacao
ORDER BY id_municipio;

INSERT INTO fato_indicador_municipal (id_municipio, id_indicador, ano, valor)
SELECT
    r.id_municipio,
    i.id_indicador,
    r.ano,
    r.valor
FROM raw_municipios_com_populacao r
JOIN indicadores i
    ON i.nome_indicador = r.indicador;
