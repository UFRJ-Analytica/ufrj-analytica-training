PRAGMA foreign_keys = ON; 
DROP TABLE IF EXISTS fato_indicador_municipal;
DROP TABLE IF EXISTS indicadores;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

CREATE TABLE regioes ( 
	id_regiao INTEGER PRIMARY KEY,
	sigla_regiao TEXT NOT NULL,
	nome_regiao TEXT NOT NULL
);

CREATE  TABLE estados(
	id_uf INTEGER PRIMARY KEY,
	sigla_uf TEXT NOT NULL,
	nome_uf TEXT NOT NULL,
	id_regiao INTEGER NOT NULL,
	
	FOREIGN KEY(id_regiao)
		REFERENCES regioes(id_regiao)
);

CREATE TABLE municipios(
	id_municipio INTEGER PRIMARY KEY,
	nome_municipio TEXT NOT NULL,
	id_uf INTEGER NOT NULL,
		
		FOREIGN KEY(id_uf)
			REFERENCES estados(id_uf)
);

CREATE TABLE indicadores (
    id_indicador INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_indicador TEXT NOT NULL, 
    unidade TEXT,                 
    fonte TEXT                    
);

CREATE TABLE fato_indicador_municipal (
    id_municipio INTEGER NOT NULL,
    id_indicador INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    valor FLOAT,
    PRIMARY KEY (id_municipio, id_indicador, ano),
    FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio),
    FOREIGN KEY (id_indicador) REFERENCES indicadores (id_indicador)
);