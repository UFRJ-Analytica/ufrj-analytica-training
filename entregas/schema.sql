-- schema.sql
-- UFRJ Analytica - Banco de Dados I
-- Trainee: Lucas Contreiras
-- Modelo relacional normalizado a partir das tabelas raw_

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS populacao_municipal;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

-- Regiões do Brasil (Norte, Nordeste, Sudeste, Sul, Centro-Oeste)
CREATE TABLE regioes (
    id_regiao INTEGER PRIMARY KEY,
    sigla_regiao TEXT NOT NULL,
    nome_regiao TEXT NOT NULL
);

-- Estados (UFs), cada um pertence a uma região
CREATE TABLE estados (
    id_uf INTEGER PRIMARY KEY,
    sigla_uf TEXT NOT NULL,
    nome_uf TEXT NOT NULL,
    id_regiao INTEGER NOT NULL,
    FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

-- Municípios, cada um pertence a um estado
CREATE TABLE municipios (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    id_uf INTEGER NOT NULL,
    FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

-- População por município e ano (série histórica)
CREATE TABLE populacao_municipal (
    id_municipio INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    populacao INTEGER NOT NULL,
    PRIMARY KEY (id_municipio, ano),
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);
