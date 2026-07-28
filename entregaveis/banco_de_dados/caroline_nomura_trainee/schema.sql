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
    FOREIGN KEY (id_regiao) REFERENCES regioes (id_regiao)
);

CREATE TABLE municipios (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    id_uf INTEGER NOT NULL,
    FOREIGN KEY (id_uf) REFERENCES estados (id_uf)
);

CREATE TABLE populacao_municipal (
    id_municipio INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    indicador TEXT,
    valor REAL,
    unidade TEXT,
    fonte TEXT,
    PRIMARY KEY (id_municipio, ano),
    FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio)
);