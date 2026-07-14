-- Schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS populacao_municipal;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;



CREATE TABLE regioes (
    id_regiao INTEGER PRIMARY KEY,
    sigla_regiao TEXT NOT NULL,
    nome_regiao TEXT NOT NULL
);



CREATE TABLE estados (
    id_uf INTEGER PRIMARY KEY,
    sigla_uf TEXT NOT NULL,
    nome_uf TEXT NOT NULL,
    id_regiao INTEGER NOT NULL,

    FOREIGN KEY (id_regiao)
        REFERENCES regioes(id_regiao)
);



CREATE TABLE municipios (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    id_uf INTEGER NOT NULL,

    FOREIGN KEY (id_uf)
        REFERENCES estados(id_uf)
);



CREATE TABLE populacao_municipal (
    id_municipio INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    indicador TEXT NOT NULL,
    valor INTEGER,
    unidade TEXT,
    fonte TEXT,

    PRIMARY KEY (id_municipio, ano, indicador),

    FOREIGN KEY (id_municipio)
        REFERENCES municipios(id_municipio)
);




-- Carga.sql 
PRAGMA foreign_keys = ON;

INSERT INTO regioes (
    id_regiao,
    sigla_regiao,
    nome_regiao
)
SELECT DISTINCT
    id_regiao,
    sigla_regiao,
    nome_regiao
FROM raw_regioes
WHERE id_regiao IS NOT NULL;



INSERT INTO estados (
    id_uf,
    sigla_uf,
    nome_uf,
    id_regiao
)
SELECT DISTINCT
    id_uf,
    sigla_uf,
    nome_uf,
    id_regiao
FROM raw_estados
WHERE id_uf IS NOT NULL
  AND id_regiao IS NOT NULL;



INSERT INTO municipios (
    id_municipio,
    nome_municipio,
    id_uf
)
SELECT DISTINCT
    id_municipio,
    nome_municipio,
    id_uf
FROM raw_municipios
WHERE id_municipio IS NOT NULL
  AND id_uf IS NOT NULL;



INSERT INTO populacao_municipal (
    id_municipio,
    ano,
    indicador,
    valor,
    unidade,
    fonte
)
SELECT DISTINCT
    id_municipio,
    ano,
    indicador,
    valor,
    unidade,
    fonte
FROM raw_populacao_municipal
WHERE id_municipio IS NOT NULL
  AND ano IS NOT NULL
  AND indicador IS NOT NULL;
