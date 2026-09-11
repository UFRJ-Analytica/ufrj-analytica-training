DROP TABLE IF EXISTS cadastros_municipais;

CREATE TABLE cadastros_municipais (
    id_cadastro_municipal INTEGER PRIMARY KEY,
    status_atual TEXT NOT NULL,
    prioridade TEXT NOT NULL,
    responsavel TEXT NOT NULL,

    id_municipio INT,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipios) 
);


INSERT INTO cadastros_municipais(status_atual, prioridade, responsavel, id_municipio)
    VALUES('Ok', 'Alta', 'Antedegmon', 1100015)