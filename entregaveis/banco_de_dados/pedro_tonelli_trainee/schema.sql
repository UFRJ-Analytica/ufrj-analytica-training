-- schema.sql
-- Modelo relacional normalizado (3FN) para os dados do IBGE.
--
-- Hierarquia geografica: regioes -> estados -> municipios
-- Fatos: fato_indicador_municipal (tabela fato) referenciando municipios
-- e uma tabela de dimensao indicadores (evita repetir texto/unidade/fonte
-- em cada uma das 5570 linhas de populacao).
--
-- Origem dos dados (tabelas raw_ criadas por load_raw_to_sqlite.py):
--   raw_regioes, raw_estados, raw_municipios,
--   raw_populacao_municipal, raw_municipios_com_populacao

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fato_indicador_municipal;
DROP TABLE IF EXISTS indicadores;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

CREATE TABLE regioes (
    id_regiao       INTEGER PRIMARY KEY,
    sigla_regiao    TEXT NOT NULL,
    nome_regiao     TEXT NOT NULL
);

CREATE TABLE estados (
    id_uf           INTEGER PRIMARY KEY,
    sigla_uf        TEXT NOT NULL,
    nome_uf         TEXT NOT NULL,
    id_regiao       INTEGER NOT NULL,
    FOREIGN KEY (id_regiao) REFERENCES regioes (id_regiao)
);

CREATE TABLE municipios (
    id_municipio    INTEGER PRIMARY KEY,
    nome_municipio  TEXT NOT NULL,
    id_uf           INTEGER NOT NULL,
    FOREIGN KEY (id_uf) REFERENCES estados (id_uf)
);

-- Dimensao de indicadores: hoje so existe "populacao_residente_estimada",
-- mas a tabela permite adicionar outros indicadores do IBGE no futuro
-- sem alterar o esquema (ex.: PIB per capita, IDH, area territorial).
CREATE TABLE indicadores (
    id_indicador    INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo          TEXT NOT NULL UNIQUE,
    unidade         TEXT,
    fonte           TEXT
);

-- Tabela fato: um valor por municipio, indicador e ano.
CREATE TABLE fato_indicador_municipal (
    id_municipio    INTEGER NOT NULL,
    id_indicador    INTEGER NOT NULL,
    ano             INTEGER NOT NULL,
    valor           REAL NOT NULL,
    PRIMARY KEY (id_municipio, id_indicador, ano),
    FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio),
    FOREIGN KEY (id_indicador) REFERENCES indicadores (id_indicador)
);
