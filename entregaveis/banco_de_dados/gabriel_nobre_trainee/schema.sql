-- schema.sql
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fato_indicador_municipal;
DROP TABLE IF EXISTS indicadores;
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

CREATE TABLE indicadores (
    indicador TEXT PRIMARY KEY,
    unidade TEXT NOT NULL,
    fonte TEXT NOT NULL

);

CREATE TABLE fato_indicador_municipal (
id_municipio BIGINT REFERENCES municipios(id_municipio),
valor FLOAT NOT NULL,
indicador TEXT REFERENCES indicadores(indicador),
ano INT NOT NULL,
PRIMARY KEY (id_municipio, ano, indicador)

);
