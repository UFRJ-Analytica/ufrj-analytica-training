-- schema.sql
-- Defina aqui a estrutura do banco de dados normalizado.

-- Ativar chaves estrangeiras
PRAGMA foreign_keys = ON;

-- Limpeza das tabelas finais (se já existirem) -> "reexecutavel"
DROP TABLE IF EXISTS populacao;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

-- Criação de tabelas finais
CREATE TABLE regioes(
    id_regiao INTEGER PRIMARY KEY,
    sigla_regiao TEXT NOT NULL,
    nome_regiao TEXT NOT NULL
);

CREATE TABLE estados(
    id_uf INTEGER PRIMARY KEY,
    sigla_uf TEXT NOT NULL,
    nome_uf TEXT NOT NULL,
    id_regiao INTEGER NOT NULL, 
    FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

CREATE TABLE municipios(
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    id_uf INTEGER NOT NULL,
    FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

CREATE TABLE populacao(
    id_municipio INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    valor_populacao INTEGER,
    PRIMARY KEY(id_municipio, ano),
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
); -- Usar o ano como primary key faz sentido se considerarmos a possibilidade de adicionar outros anos no bd