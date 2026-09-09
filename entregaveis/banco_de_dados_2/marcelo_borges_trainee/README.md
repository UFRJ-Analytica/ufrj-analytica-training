# Banco de Dados II - Analytica

## Investigação sobre possível manipulação de resultados na Polymarket

### Marcelo Henrique Machado Rieke Borges

**Arquivos `.csv` utilizados no relatório:**  
https://drive.google.com/drive/folders/1BjYNZ6SPx96NHHkhuDLJFQc0sdN4PofD?usp=sharing

## Introdução

Este relatório resume a investigação desenvolvida no arquivo `relatorio.ipynb`, baseada em uma reportagem da Fortune Media sobre um possível caso de aposta com benefício próprio na Polymarket. De acordo com a notícia, um apostador teria se beneficiado por possuir informações privilegiadas sobre a captura do então presidente venezuelano Nicolás Maduro pelo governo dos Estados Unidos, ocorrida em **03/01/2026 às 06:00 UTC**.

**Fonte:** https://www.infomoney.com.br/business/global/trader-fatura-r-2-milhoes-no-polymarket-apostando-na-queda-de-maduro-no-dia-da-acao/

## Seleção do mercado

Em primeiro lugar, foram buscados no dataset mercados cujos títulos contivessem a substring **"maduro"** e que estivessem relacionados à possível queda do então presidente venezuelano.

Entre os resultados encontrados, foi selecionado o mercado com o maior volume de negociações, intitulado **"Maduro out by January 31, 2026?"**.

Esse mercado teve início em **12/12/2025** e, embora estivesse programado para permanecer ativo até o fim de janeiro, foi encerrado antecipadamente após a captura de Maduro, em **03/01/2026**.

## Objetivo

A investigação busca responder à seguinte pergunta central:

> Com base nos dados disponibilizados, é possível reconhecer padrões anormais de negociação que indiquem a atuação de usuários com informações privilegiadas?

A hipótese inicial é que seja possível identificar comportamentos atípicos de negociação, especialmente em datas próximas à captura de Maduro. No entanto, talvez os dados disponíveis não sejam suficientes para afirmar, de forma categórica, que tais padrões representem a existência de apostadores com informações privilegiadas.

Para responder a essa pergunta, serão analisados o comportamento das negociações relacionadas ao evento e os padrões de atuação dos usuários com maior relevância financeira ao longo da vida do mercado.