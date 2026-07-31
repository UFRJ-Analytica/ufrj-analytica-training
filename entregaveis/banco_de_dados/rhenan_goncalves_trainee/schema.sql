-- normalizacao.sql
-- Crie aqui as tabelas normalizadas e popule a partir das tabelas raw_.
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS censo;
DROP TABLE IF EXISTS Municipios;
DROP TABLE IF EXISTS UF;
DROP TABLE IF EXISTS regiao;
DROP TABLE IF EXISTS fonte;

CREATE TABLE fonte 
( 
 id_fonte INTEGER PRIMARY KEY AUTOINCREMENT,  
 nome VARCHAR(200) NOT NULL
); 

CREATE TABLE regiao 
( 
 id_regiao INT PRIMARY KEY,  
 nome_regiao VARCHAR(50),  
 sigla_regiao CHAR(2)
); 

CREATE TABLE UF 
( 
 id_uf INT PRIMARY KEY,  
 id_regiao INT NOT NULL,  
 nome_uf VARCHAR(50),  
 sigla_uf CHAR(2),  
 UNIQUE (nome_uf),
 UNIQUE (sigla_uf),
 FOREIGN KEY (id_regiao) REFERENCES regiao (id_regiao)
); 

CREATE TABLE Municipios 
( 
 id_municipio INT PRIMARY KEY,  
 id_uf INT NOT NULL,  
 nome_municipio VARCHAR(50),
 FOREIGN KEY (id_uf) REFERENCES UF (id_uf)
); 

CREATE TABLE censo 
( 
 Ano INT,  
 id_fonte INT,  
 id_municipio INT,  
 valor INT NOT NULL,
 PRIMARY KEY (Ano, id_fonte, id_municipio),
 FOREIGN KEY (id_fonte) REFERENCES fonte (id_fonte),
 FOREIGN KEY (id_municipio) REFERENCES Municipios (id_municipio)
);

-- Exemplo de estrutura esperada:
-- DROP TABLE IF EXISTS ...
-- CREATE TABLE ...
-- INSERT INTO ... SELECT ...
