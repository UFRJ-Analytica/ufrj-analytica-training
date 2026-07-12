-- analytics.sql
-- Escreva aqui consultas analíticas ou uma proposta de camada analítica.
-- Exemplos: rankings, agregações por região/UF, views, tabela fato/dimensões.


-- Quais são os municípios mais populosos da base?
SELECT DISTINCT
    muni.nome_municipio Município,
    pop.valor População
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
    ORDER BY População DESC
    LIMIT 10;
-- Os 3 municípios mais populosos são São Paulo, Rio de Janeiro e Braília, seguido
-- por alguns outros que podem ser vistos na query. Ordenando a população em ordem 
-- decrescente, podemos pegar as primeiras entrar para descobrir o município mais
-- populoso. 


-- Quais são os municípios mais populosos de uma UF escolhida (RO)?
SELECT DISTINCT
    muni.nome_municipio Município,
    pop.valor População
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
    WHERE muni.id_uf=
        (SELECT id_uf FROM estados WHERE estados.sigla_uf = 'RO')
    ORDER BY População DESC
    LIMIT 10;
-- Os 3 municípios mais populosos de RO são Porto Velho, Ji-Paraná e Vilhena, seguido
-- por alguns outros que podem ser vistos na query. Ordenando a população em ordem 
-- decrescente, podemos pegar as primeiras entrar para descobrir o município mais
-- populoso. Usamos uma query secundária para encontrar o id de RO sem procurar na
-- tabela manualmente


-- Qual é a população total estimada por região?
SELECT DISTINCT
    reg.nome_regiao Região,
    sum(pop.valor) "População Total"
    FROM regioes reg
        NATURAL JOIN estados
        NATURAL JOIN municipios
        NATURAL JOIN populacao_municipal pop
    GROUP BY reg.id_regiao
    ORDER BY Região;
-- Ligamos a região com a população municipal através de joins nas tabelas intermediárias,
-- agrupamos pelas regiões e somamos as populações. A resposta pode ser vista na tabela 
-- da query.


-- Qual é a população média dos municípios por estado?
SELECT DISTINCT
    est.nome_uf Estado,
    avg(pop.valor) "População Média"
    FROM estados est
        NATURAL JOIN municipios
        NATURAL JOIN populacao_municipal pop
    GROUP BY est.id_uf
    ORDER BY Estado;
-- Mesma coisa que na pergunta anterior, porém com estado no lugar de região e média no 
-- lugar de soma. A resposta pode ser vista da saída da query.


-- Quais municípios possuem população acima da média nacional dos municípios?
SELECT avg(valor) FROM populacao_municipal;

SELECT DISTINCT
    muni.nome_municipio Municipio,
    pop.valor População
    FROM municipios muni
        NATURAL JOIN populacao_municipal pop
    WHERE pop.valor > (SELECT avg(valor) FROM populacao_municipal)
    LIMIT 30;
-- Fazemos um filtro no valor da população com base em um query segundária que calcula a 
-- média populacional de todos os municípios. A resposta pode ser vista na saída da query.