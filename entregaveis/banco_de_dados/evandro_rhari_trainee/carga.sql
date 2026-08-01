-- carg.sql
-- Crie aqui as tabelas normalizadas e popule a partir das tabelas raw_.
-- Para os comandos INSERT INTO ... SELECT

PRAGMA foreign_keys = ON;

-- Exemplo de estrutura esperada:
-- DROP TABLE IF EXISTS ...
-- CREATE TABLE ...
-- INSERT INTO ... SELECT ...


INSERT INTO regioes (
    id_regiao,
    sigla_regiao,
    nome_regiao
)
    SELECT DISTINCT
            id_regiao,
            sigla_regiao,
            nome_regiao
        FROM raw_regioes
        WHERE id_regiao IS NOT NULL;


INSERT INTO estados (
    id_uf,
    sigla_uf,
    nome_uf,
    id_regiao
)
    SELECT DISTINCT 
            id_uf,
            sigla_uf,
            nome_uf,
            id_regiao
        FROM raw_estados
        WHERE id_uf IS NOT NULL AND id_regiao IS NOT NULL;


INSERT INTO municipios (
    id_municipio,
    nome_municipio,
    id_uf
)
    SELECT DISTINCT 
            id_municipio,
            nome_municipio,
            id_uf
        FROM raw_municipios
        WHERE id_municipio IS NOT NULL AND id_uf IS NOT NULL;


INSERT INTO populacao_municipal (
    -- o id_pop_inicial é preenchido automaticamente
    ano,
    indicador,
    valor,
    unidade,
    fonte,
    id_municipio
)
    SELECT DISTINCT
            ano,
            indicador,
            valor,
            unidade,
            fonte,
            id_municipio
        FROM raw_populacao_municipal
        WHERE id_municipio IS NOT NULL; 