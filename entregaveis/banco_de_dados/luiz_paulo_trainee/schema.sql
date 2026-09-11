-- schema.sql
-- Defina aqui a estrutura do banco de dados normalizado.
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS relatorio_populacao;
DROP TABLE IF EXISTS municipio;
DROP TABLE IF EXISTS estado;
DROP TABLE IF EXISTS regiao;

--criando entidades fortes:
CREATE TABLE regiao(
    id BIGINT PRIMARY KEY,
    sigla TEXT,
    nome TEXT
);

CREATE TABLE estado(
    id BIGINT PRIMARY KEY,
    sigla TEXT,
    nome TEXT,
    id_regiao BIGINT,

    FOREIGN KEY (id_regiao) REFERENCES regiao(id)
);

CREATE TABLE municipio(
    id BIGINT PRIMARY KEY,
    nome TEXT,
    id_estado BIGINT,

    FOREIGN KEY (id_estado) REFERENCES estado(id)
);

CREATE TABLE relatorio_populacao(
    ano BIGINT,
    id_municipio BIGINT,
    indicador TEXT,
    valor FLOAT,
    unidade TEXT,
    fonte TEXT,

    PRIMARY KEY (ano, id_municipio),

    FOREIGN KEY (id_municipio) REFERENCES municipio(id)
);