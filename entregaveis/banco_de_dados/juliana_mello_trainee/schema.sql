-- schema.sql
-- Defina aqui a estrutura do banco de dados normalizado.

PRAGMA foreign_keys = ON;

-- tabelas "raw" são tabelas "cruas", podendo ter dados repetidos, desorganizados, misturados


-- se mudar algo nas tabelas que já existem, vai apagar e depois criar nova
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
    id_uf BIGINT PRIMARY KEY,
    sigla_uf TEXT NOT NULL,
    nome_uf TEXT NOT NULL,
    id_regiao BIGINT NOT NULL,
    -- sigla_regiao INTEGER NOT NULL, se informação ja tem em outra tabela, so coloca o id dessa outra como FK
    -- nome_regiao INTEGER NOT NULL, se precisar saber o nome ou sigla, vai olha na tabela regioes usando id_regioes
    FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

CREATE TABLE municipios (
    id_municipio BIGINT PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    -- id_regiao BIGINT NOT NULL, ja dá pra chegar na regiao com a referência do estado
    -- FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao),
    id_uf BIGINT NOT NULL,
    FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

CREATE TABLE populacao_municipal (
    ano BIGINT NOT NULL,
    indicador TEXT NOT NULL,
    valor FLOAT NOT NULL,
    unidade TEXT NOT NULL,
    fonte TEXT NOT NULL,
    id_municipio BIGINT NOT NULL,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);