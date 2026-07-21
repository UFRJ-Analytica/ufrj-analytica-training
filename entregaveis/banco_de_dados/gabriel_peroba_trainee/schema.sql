PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS populacao_municipal;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

-- Tabela de Regioes
CREATE TABLE regioes (
    id_regiao INTEGER PRIMARY KEY,
    sigla_regiao TEXT NOT NULL,
    nome_regiao TEXT NOT NULL
);

-- 2. Tabela de Estados
CREATE TABLE estados (
    id_uf INTEGER PRIMARY KEY,
    sigla_uf TEXT NOT NULL,
    nome_uf TEXT NOT NULL,
    id_regiao INTEGER,
    FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

-- Tabela de Municipios
CREATE TABLE municipios (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    id_uf INTEGER,
    FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

-- 4. Tabela de Populacao
CREATE TABLE populacao_municipal (
    id_municipio INTEGER,
    ano INTEGER,
    indicador TEXT,
    valor REAL,
    unidade TEXT,
    fonte TEXT,
    PRIMARY KEY (id_municipio, ano, indicador), -- Chave composta (um município pode ter vários anos/indicadores)
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);