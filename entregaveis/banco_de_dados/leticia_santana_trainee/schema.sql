PRAGMA foreign_keys = ON;

CREATE TABLE REGIOES(
		id_regiao INTEGER PRIMARY KEY,
		sigla_regiao TEXT NOT NULL,
		nome_regiao TEXT NOT  NULL
);

CREATE TABLE ESTADOS(
		id_uf INTEGER PRIMARY KEY,
		sigla_uf TEXT NOT NULL,
		nome_uf TEXT NOT NULL, 
		id_regiao INTEGER NOT NULL,
		
		FOREIGN KEY(id_regiao) REFERENCES REGIOES(id_regiao)
);

CREATE TABLE MUNICIPIOS(
		id_municipio INTEGER PRIMARY KEY,
		nome_municipio TEXT NOT NULL,
		id_uf INTEGER NOT NULL,
		
		FOREIGN KEY(id_uf) REFERENCES ESTADOS(id_uf)
);

CREATE TABLE POPULACOES(
		id_municipio INTEGER NOT NULL,
		ano INTEGER NOT NULL,
		indicador TEXT NOT NULL,
		valor REAL NOT NULL,
		unidade TEXT NOT NULL,
		fonte TEXT NOT NULL,
		
		PRIMARY KEY (id_municipio, ano, indicador),
		FOREIGN KEY(id_municipio) REFERENCES MUNICIPIOS(id_municipio)
);
