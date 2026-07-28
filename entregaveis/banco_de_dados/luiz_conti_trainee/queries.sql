-- queries.sql

--1. Quais regiões existem na base?
--Resposta: 5 regiões

SELECT COUNT(id_regiao) FROM regioes;

--2. Quais estados pertencem a uma região escolhida?
--Região escolhida: Sudeste (id 3)

--Resposta: Rio de Janeiro, Minas Gerais, São Paulo, Espírito Santo

SELECT nome_uf 
	FROM regioes
	INNER JOIN estados
		ON estados.id_regiao = regioes.id_regiao
	WHERE estados.id_regiao = 3; 

--3. Quais municípios pertencem a uma UF escolhida?
--UF escolhida: Acre (id 12)

--Resposta: Acrelândia, Assis, Brasil, Brasiléia, Bujari, Capixaba, Cruzeiro do Sul, Epitaciolândia
--Feijó, Jordão, Mâncio Lima, Manoel Urbano, Marechal Thaumaturgo, Plácido de Castro, Porto Walter,
--Rio Branco, Rodrigues Alves, Santa Rosa do Purus, Senador Guiomard, Sena Madureira, Tarauacá, Xapuri, Porto Acre,

SELECT nome_municipio
	FROM municipios
	INNER JOIN estados 
		ON municipios.id_uf = estados.id_uf 
	WHERE municipios.id_uf = 12; 

--4. Qual é o estado e a região de cada município?

--Como a resposta é enorme, mostrarei apenas um exemplo:

--Município: Alta Floresta D'Oeste
--Região: Norte
--Estado: Rondônia

SELECT nome_regiao, nome_uf, nome_municipio 
	FROM regioes 
	INNER JOIN estados 
		ON estados.id_regiao = regioes.id_regiao 
	INNER JOIN municipios
		ON municipios.id_uf = estados.id_uf; 

--5. Qual é a população estimada dos municípios, mostrando município, UF, região, ano e valor?

--Como a resposta é enorme, mostrarei apenas um exemplo:

--Município: Tapauá

--Região: Norte

--UF: Amazonas

--Ano: 2025

--Valor: 20.728

SELECT nome_municipio, nome_uf, nome_regiao, ano, valor
	FROM regioes
	INNER JOIN estados 
		ON estados.id_regiao = regioes.id_regiao 
	INNER JOIN municipios
		ON municipios.id_uf = estados.id_uf 
	INNER JOIN fato_indicador_municipal
		ON fato_indicador_municipal.id_municipio = municipios.id_municipio;

--6. Quantos municípios existem por estado?

--Resposta:
	
--Rondônia	52
--Acre	22
--Amazonas	62
--Roraima	15
--Pará	144
--Amapá	16
--Tocantins	139
--Maranhão	217
--Piauí	224
--Ceará	184
--Rio Grande do Norte	167
--Paraíba	223
--Pernambuco	185
--Alagoas	102
--Sergipe	75
--Bahia	417
--Minas Gerais	853
--Espírito Santo	78
--Rio de Janeiro	92
--São Paulo	645
--Paraná	399
--Santa Catarina	295
--Rio Grande do Sul	497
--Mato Grosso do Sul	79
--Mato Grosso	141
--Goiás	246
--Distrito Federal	1
	
SELECT nome_uf, COUNT(id_municipio)
	FROM municipios
	INNER JOIN estados
		ON municipios.id_uf = estados.id_uf
	GROUP BY estados.id_uf;

--7. Quantos municípios existem por região?

--Resposta:

--Norte:	450
--Nordeste:	1794
--Sudeste:	1668
--Sul:	1191
--Centro-Oeste:	467

SELECT nome_regiao, COUNT(id_municipio)
	FROM municipios
	INNER JOIN estados
		ON municipios.id_uf = estados.id_uf
	INNER JOIN regioes
		ON estados.id_regiao = regioes.id_regiao  
	GROUP BY regioes.id_regiao;

--8. Qual é a população total estimada por estado?

--Resposta: 
--Rondônia	1751950
--Acre	884372
--Amazonas	4321616
--Roraima	738772
--Pará	8711196
--Amapá	806517
--Tocantins	1586859
--Maranhão	7018211
--Piauí	3384547
--Ceará	9268836
--Rio Grande do Norte	3455236
--Paraíba	4164468
--Pernambuco	9562007
--Alagoas	3220848
--Sergipe	2299425
--Bahia	14870907
--Minas Gerais	21393441
--Espírito Santo	4126854
--Rio de Janeiro	17223547
--São Paulo	46081801
--Paraná	11890517
--Santa Catarina	8187029
--Rio Grande do Sul	11233263
--Mato Grosso do Sul	2924631
--Mato Grosso	3887782
--Goiás	7423629
--Distrito Federal	2996899

SELECT nome_uf, SUM(valor)
	FROM estados
	INNER JOIN municipios
		ON municipios.id_uf = estados.id_uf 
	INNER JOIN fato_indicador_municipal
		ON fato_indicador_municipal.id_municipio = municipios.id_municipio
	GROUP BY estados.id_uf;
	

--9. Quais estados possuem uma quantidade elevada de municípios (Top 10 Estados)?

--Resposta:
--1.  Minas Gerais
--2.  São Paulo
--3.  Rio Grande do Sul
--4.  Bahia
--5.  Paraná
--6.  Santa Catarina
--7.  Goiás
--8.  Piauí
--9.  Paraíba
--10. Maranhão

SELECT nome_uf, COUNT(id_municipio) as qtd_municipios
	FROM municipios
	INNER JOIN estados
		ON municipios.id_uf = estados.id_uf
	GROUP BY estados.id_uf
	ORDER BY qtd_municipios DESC
	LIMIT 10;

--10. Crie uma tabela simples de teste e registre uma inserção, uma alteração e uma remoção de registro nessa tabela.

DROP TABLE IF EXISTS paises;

CREATE TABLE paises (

	id_pais INTEGER PRIMARY KEY,
	nome_pais TEXT NOT NULL,
	sigla_pais TEXT NOT NULL
);

INSERT INTO paises (nome_pais, sigla_pais) VALUES ("Brazil", "BR");

UPDATE paises SET nome_pais = "Brasil", sigla_pais = "BRA"
WHERE nome_pais = "Brazil";

DELETE FROM paises 
WHERE nome_pais = "Brasil";

SELECT * FROM paises;


