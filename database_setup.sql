-- database_setup.sql
-- Migra o database.db (herdado da entrega de BD1) para o schema oficial
-- esperado pela API da tarefa de WebDev (backend/app/main.py, tarefa.md,
-- apostila.md) e recria a tabela de cadastro do gestor.
--
-- Rode este script com o database.db da raiz do repo já sendo uma cópia
-- de entregaveis/banco_de_dados/luiz_paulo_trainee/database.db (schema em
-- regiao/estado/municipio/relatorio_populacao, no singular).
--
-- O dado não muda, só é migrado de nome de tabela/coluna. Ao final, sobram
-- exatamente 5 tabelas: regioes, estados, municipios, populacao_municipal
-- e registros_gestor.

PRAGMA foreign_keys = ON;

-- 1) Schema oficial esperado pela API (nomes/colunas de main.py + apostila.md).
DROP TABLE IF EXISTS regioes;
CREATE TABLE regioes (
    id_regiao    BIGINT PRIMARY KEY,
    sigla_regiao TEXT,
    nome_regiao  TEXT
);

DROP TABLE IF EXISTS estados;
CREATE TABLE estados (
    id_uf      BIGINT PRIMARY KEY,
    sigla_uf   TEXT,
    nome_uf    TEXT,
    id_regiao  BIGINT,
    FOREIGN KEY (id_regiao) REFERENCES regioes(id_regiao)
);

DROP TABLE IF EXISTS municipios;
CREATE TABLE municipios (
    id_municipio   BIGINT PRIMARY KEY,
    nome_municipio TEXT,
    id_uf          BIGINT,
    FOREIGN KEY (id_uf) REFERENCES estados(id_uf)
);

DROP TABLE IF EXISTS populacao_municipal;
CREATE TABLE populacao_municipal (
    id_municipio BIGINT NOT NULL,
    ano          BIGINT NOT NULL,
    indicador    TEXT,
    valor        FLOAT,
    unidade      TEXT,
    fonte        TEXT,
    PRIMARY KEY (id_municipio, ano),
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);

-- 2) Migra o dado já validado em BD1 (regiao/estado/municipio/
--    relatorio_populacao) pro schema acima - só renomeia tabela/coluna,
--    o dado não muda.
INSERT INTO regioes (id_regiao, sigla_regiao, nome_regiao)
SELECT id, sigla, nome FROM regiao;

INSERT INTO estados (id_uf, sigla_uf, nome_uf, id_regiao)
SELECT id, sigla, nome, id_regiao FROM estado;

INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
SELECT id, nome, id_estado FROM municipio;

INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
SELECT id_municipio, ano, indicador, valor, unidade, fonte FROM relatorio_populacao;

-- 3) Cadastro do gestor (Parte 1 do tarefa.md) - FK atualizada pro novo
--    nome da tabela de municípios. Recriada do zero: está vazia nas duas
--    cópias existentes, então não perde nada, e já aplica INTEGER PRIMARY
--    KEY (autoincrementa sozinho no SQLite; BIGINT PRIMARY KEY não).
DROP TABLE IF EXISTS registros_gestor;
CREATE TABLE registros_gestor (
    id_registro    INTEGER PRIMARY KEY,
    id_municipio   BIGINT NOT NULL,
    status         TEXT,
    prioridade     TEXT,
    observacao     TEXT,
    responsavel    TEXT,
    data_registro  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio) ON DELETE CASCADE
);

-- 4) Remove o que não é mais necessário: tabelas antigas no singular (já
--    migradas no passo 2) e staging do ETL de BD1.
DROP TABLE IF EXISTS relatorio_populacao;
DROP TABLE IF EXISTS municipio;
DROP TABLE IF EXISTS estado;
DROP TABLE IF EXISTS regiao;
DROP TABLE IF EXISTS raw_municipios_com_populacao;
DROP TABLE IF EXISTS raw_populacao_municipal;
DROP TABLE IF EXISTS raw_municipios;
DROP TABLE IF EXISTS raw_estados;
DROP TABLE IF EXISTS raw_regioes;
DROP TABLE IF EXISTS metadata_carga;
