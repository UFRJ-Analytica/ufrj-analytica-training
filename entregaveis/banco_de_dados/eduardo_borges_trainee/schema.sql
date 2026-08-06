-- 1. Tabela regioes
CREATE TABLE regioes (
    id_regiao INTEGER PRIMARY KEY,
    sigla_regiao TEXT NOT NULL,
    nome_regiao TEXT NOT NULL
);

-- 2. Tabela estados
CREATE TABLE estados (
    id_uf INTEGER PRIMARY KEY,
    nome_uf TEXT NOT NULL,
    sigla_uf TEXT NOT NULL,
    id_regiao INTEGER,
    FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

-- 3. Tabela municipios
CREATE TABLE municipios (
    id_municipio INTEGER PRIMARY KEY,
    nome_municipio TEXT NOT NULL,
    id_uf INTEGER,
    FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

-- 4. Tabela indicadores
CREATE TABLE indicadores (
    id_indicador INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_indicador TEXT NOT NULL
);

-- 5. Tabela fato_indicador_municipal
CREATE TABLE fato_indicador_municipal (
    id_municipio INTEGER,
    id_indicador INTEGER,
    ano INTEGER,
    valor INTEGER,
    PRIMARY KEY (id_municipio, id_indicador, ano),
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio),
    FOREIGN KEY (id_indicador) REFERENCES indicadores(id_indicador)
);