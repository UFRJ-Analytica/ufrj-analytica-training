PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS recenseamento;
DROP TABLE IF EXISTS censos;
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
 FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

CREATE TABLE municipios (
 id_municipio INTEGER PRIMARY KEY,
 nome_municipio TEXT NOT NULL,
 id_uf INTEGER NOT NULL,
 FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

CREATE TABLE censos (
 id_censo INTEGER PRIMARY KEY,
 ano INTEGER NOT NULL,
 fonte TEXT NOT NULL
);

CREATE TABLE recenseamento (
 id_municipio INTEGER,
 id_censo INTEGER,
 valor INTEGER NOT NULL,
 unidade TEXT NOT NULL,
 PRIMARY KEY(id_municipio, id_censo),
 FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio),
 FOREIGN KEY (id_censo) REFERENCES censos(id_censo)
);