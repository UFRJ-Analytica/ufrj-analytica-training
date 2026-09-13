-- schema.sql
-- Defina aqui a estrutura do banco de dados normalizado.
-- schema.sql
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS populacao_municipal;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

CREATE TABLE regioes (
id_regiao INTEGER PRIMARY KEY,
sigla_regiao TEXT NOT NULL,
nome_regiao TEXT NOT NULL
);

create table estados (
id_uf integer primary key, 
sigla_uf text not null,
nome_uf text not null,
id_regiao integer not null,
foreign key (id_regiao) references regioes (id_regiao)
);

create table municipios (
id_municipio integer primary key,
nome_municipio text not null,
id_uf integer not null,
foreign key (id_uf) references estados (id_uf)
);

create table populacao_municipal (
id_municipio integer not null,
ano integer not null,
valor integer not null,
primary key (id_municipio,ano),
foreign key (id_municipio) references municipios(id_municipio)
);

