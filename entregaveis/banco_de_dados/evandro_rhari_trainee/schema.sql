-- schema.sql
-- Crie aqui as tabelas normalizadas e popule a partir das tabelas raw_.
-- Para os comandos DROP/CREATE TABLE


PRAGMA foreign_keys = ON;

-- Exemplo de estrutura esperada:
-- DROP TABLE IF EXISTS ...
-- CREATE TABLE ...


DROP TABLE IF EXISTS populacao_municipal;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;



CREATE TABLE regioes (
    id_regiao INT PRIMARY KEY,
    sigla_regiao TEXT NOT NULL,
    nome_regiao TEXT NOT NULL
);


CREATE TABLE estados (
    id_uf INT PRIMARY KEY,
    sigla_uf TEXT NOT NULL,
    nome_uf TEXT NOT NULL,

    id_regiao INT NOT NULL,
    FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);


CREATE TABLE municipios (
    id_municipio BIGINT PRIMARY KEY,
    nome_municipio TEXT NOT NULL,

    id_uf INT NOT NULL,
    FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);


CREATE TABLE populacao_municipal (
    id_pop_municipal INTEGER PRIMARY KEY,
    ano BIGINT NOT NULL,
    indicador TEXT NOT NULL,
    valor FLOAT NOT NULL,
    unidade TEXT NOT NULL,
    fonte TEXT NOT NULL,

    id_municipio BIGINT NOT NULL,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);