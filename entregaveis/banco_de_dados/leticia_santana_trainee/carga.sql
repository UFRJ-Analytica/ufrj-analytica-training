INSERT INTO REGIOES (id_regiao, sigla_regiao, nome_regiao)
SELECT id_regiao, sigla_regiao, nome_regiao
FROM raw_regioes rr;

INSERT INTO ESTADOS(id_uf, sigla_uf, nome_uf, id_regiao)
SELECT id_uf, sigla_uf, nome_uf, id_regiao
FROM raw_estados re;

INSERT INTO MUNICIPIOS(id_municipio, nome_municipio, id_uf)
SELECT DISTINCT id_municipio, nome_municipio, id_uf
FROM raw_municipios rm ;

INSERT INTO POPULACOES(id_municipio, ano, indicador, valor, unidade, fonte)
SELECT DISTINCT id_municipio, ano, indicador, valor, unidade, fonte
FROM raw_populacao_municipal rpm ;