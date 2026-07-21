-- schema.sql: 
-- define estrutura da tabela, nao preenche. Fala quais sao as chaves, colunas em cada aba, colunas, como tabelasse conectam uma com outra

-- PRA SALVAR
-- integer, real e text (tipos mais comyns)
-- declara colunas --> declara primary key --> declara foreign key



PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS populacao_municipal; -- apaga filho dps pai
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS estados;
DROP TABLE IF EXISTS regioes;

CREATE TABLE regioes (
    id_regiao INTEGER PRIMARY KEY, -- integer pq recebe num inteiros, primary key pq chave primaria (Algo como 1 2 3 4 5)
    sigla_regiao TEXT NOT NULL, -- nome da coluna // text pq recebe texto // not null pq precisa ser preenchido (N NE SE)
    nome_regiao TEXT NOT NULL -- (nORTE, Nordeste, Suk, etc)
);


CREATE TABLE estados (
    id_uf INTEGER PRIMARY KEY,
    sigla_uf TEXT NOT NULL,
    nome_uf TEXT NOT NULL,

    id_regiao INTEGER NOT NULL,
    FOREIGN KEY (id_regiao) -- cria o relacionamento estados.id_regiao cm regioes.id_regiao
        REFERENCES regioes (id_regiao)
);


CREATE TABLE municipios (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,

    id_uf INTEGER NOT NULL, -- p chegar em regioes ele entra em estados e pega a regiao do estado
    FOREIGN KEY (id_uf)  REFERENCES estados (id_uf)
);


CREATE TABLE populacao_municipal (  
    id_municipio INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    indicador TEXT NOT NULL, -- mantive como not null pq vou usar na chave primaria
    valor REAL NOT NULL,
    unidade TEXT,
    fonte TEXT,

    PRIMARY KEY (id_municipio,ano,indicador), -- rio 2025 e rio 2026 tem popu != ent chave n pode ser so municipio
    
    FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio)
);
