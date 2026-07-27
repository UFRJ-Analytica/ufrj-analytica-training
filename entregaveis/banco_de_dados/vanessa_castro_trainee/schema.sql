-- schema.sql
-- tabelas normalizadas

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS populacao_municipal;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

CREATE TABLE regioes (
id_regiao INTEGER PRIMARY KEY,
nome_regiao TEXT NOT NULL,
sigla_regiao TEXT NOT NULL
);

CREATE TABLE estados (
id_uf INTEGER PRIMARY KEY,
nome_uf TEXT NOT NULL,
sigla_uf TEXT NOT NULL,
id_regiao INTEGER,
FOREIGN KEY (id_regiao) REFERENCES regioes (id_regiao)
);

CREATE TABLE municipios (
id_municipio INTEGER PRIMARY KEY,
nome_municipio TEXT NOT NULL,
id_uf INTEGER,
FOREIGN KEY (id_uf) REFERENCES estados (id_uf)
);

CREATE TABLE populacao_municipal (
id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
id_municipio INTEGER,
ano INTEGER,
indicador TEXT,
valor INTEGER,
unidade TEXT,
fonte TEXT,
FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio)
);