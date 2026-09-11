# Trabalho de Banco de Dados II - Polymarket no BigQuery

## Investigando mercado de Bitcoin (5 em 5 minutos)

#### Luiz Antônio Ferreira Conti

### Evento ou mercado escolhido

Série recorrente de mercados "Bitcoin Up or Down" de 5 em 5 minutos no Polymarket.

### Pergunta central

Os mercados de 5 minutos estão bem calibrados nos casos de alta confiança, e o volume tem padrões por hora/dia da semana e anomalias detectáveis?

### Hipótese inicial

Esperava poucos erros de calibração nas janelas de alta confiança, e que o volume variasse por horário, com volumes mais altos puxando mais oscilação de preço dentro da janela.

### Tabelas e datasets utilizados no BigQuery

Usei a tabela markets para descobrir os mercados e alguns metadados e a tabela trades para o volume real de cada mercado, já que o campo volume da tabela markets veio zerado na maioria dos casos.

### Período analisado

Março de 2026 completo, horário de New York.

### Descrição das consultas SQL e dos alertas finais

O relatório passa por consultas de exploração incial dos mercados, pela busca da família de mercados btc-updown-5m e uma consulta na tabela trades pra entender as colunas. Depois foram feitas consultas de agregação de volume, oscilação de preço e padrão por hora/dia da semana.

Nesse relatório foram construídos dois alerta, onde o primeiro pega mercados que ficaram muito confiantes de um lado (preço acima de 75% ou abaixo de 25%) mas o resultado saiu do lado oposto. O segundo compara o volume de cada janela com a média das 24 janelas anteriores, sinalizando como moderado ou extremo conforme o desvio.

A hipótese de volume se confirmou bem: pico de volume entre 9h e 12h, repetido nos dias da semana, e volume mais alto com fortes indícios de relação com uma maior oscilação e maior quantidade de negociações. A de calibração se confirmou de forma mais modesta, com poucos erros e concentrados só no lado Up.

### Link do Google Drive

https://drive.google.com/drive/folders/1aoP-GdTHE9IEOXzfaCbKom-vAamDJbyu?usp=sharing

