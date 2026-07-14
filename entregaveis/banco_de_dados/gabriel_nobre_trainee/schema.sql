-- schema.sql
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
    id_regiao BIGINT REFERENCES regioes(id_regiao)
);

CREATE TABLE municipios (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    id_uf BIGINT REFERENCES estados(id_uf)
);

CREATE TABLE populacao_municipal (
    id_municipio BIGINT REFERENCES municipios(id_municipio)
    ano BIGINT NOT NULL,
    indicador TEXT NOT NULL,
    valor FLOAT NOT NULL,
    unidade TEXT NOT NULL,
    fonte TEXT NOT NULL,
    PRIMARY KEY (id_municipio, ano, indicador)

);