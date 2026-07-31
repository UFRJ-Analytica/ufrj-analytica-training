PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS populacao_municipal;
DROP TABLE IF EXISTS municipio;
DROP TABLE IF EXISTS estado;
DROP TABLE IF EXISTS regiao;
DROP TABLE IF EXISTS censo;


CREATE TABLE regiao(
	id_regiao INTEGER PRIMARY KEY,
	sigla_regiao TEXT NOT NULL,
	nome_regiao TEXT NOT NULL
);

CREATE TABLE estado(
	id_uf INTEGER PRIMARY KEY,
	sigla_uf TEXT NOT NULL,
	nome_uf TEXT NOT NULL,
	id_regiao INTEGER NOT NULL,
	FOREIGN KEY (id_regiao) REFERENCES regiao(id_regiao)
);

CREATE TABLE municipio(
	id_municipio INTEGER PRIMARY KEY,
	nome_municipio TEXT NOT NULL,
	id_estado INTEGER NOT NULL,
	FOREIGN KEY (id_estado) REFERENCES estado(id_uf)
);

CREATE TABLE censo(
	id_censo INTEGER PRIMARY KEY,
	ano INTEGER NOT NULL,
	indicador TEXT NOT NULL,
	unidade TEXT NOT NULL,
	fonte TEXT NOT NULL
);

CREATE TABLE populacao_municipal(
	id_municipio INTEGER,
	id_censo INTEGER NOT NULL,
	valor INTEGER NOT NULL,
	PRIMARY KEY (id_municipio, id_censo)
	FOREIGN KEY (id_municipio) REFERENCES municipio(id_municipio),
	FOREIGN KEY (id_censo) REFERENCES censo(id_censo)
);