PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS populacao_municipal; 
DROP TABLE IF EXISTS municipios; 
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

CREATE TABLE regioes (
    id_regiao INTEGER PRIMARY KEY, 
    sigla_regiao TEXT, 
    nome_regiao TEXT 
);

CREATE TABLE estados(
    id_uf INTEGER PRIMARY KEY,
    sigla_uf TEXT,
    nome_uf TEXT,
    id_regiao INTEGER,
    CONSTRAINT FK_regiao FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

CREATE TABLE municipios(
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT,
    id_uf INTEGER,
    CONSTRAINT FK_estado FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

CREATE TABLE populacao_municipal(
    id_municipio INTEGER PRIMARY KEY,
    ano INTEGER,
    valor integer,
    indicador TEXT,
    unidade TEXT,
    fonte TEXT,
    CONSTRAINT FK_municipio FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);