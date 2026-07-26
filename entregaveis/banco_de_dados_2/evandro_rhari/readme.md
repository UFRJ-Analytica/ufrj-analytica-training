# Movimentação pré-eleição em mercados presidenciais --- Polymarket no BigQuery

Uma análise comparando política com futebol.
Esse trabalho é fortemente derivado do trabalho do Carlos Pereira entitulado [Movimentação pré-jogo em mercados de futebol — Polymarket no BigQuery](https://colab.research.google.com/drive/1hBLufaANuG5hQ0Lfs9_RVlRaIGG7yRcb?usp=sharing#scrollTo=aqJgBjqUkyGD). Para entender esse projeto, é necesssário acompanhar o projeto do Carlos.

## Informações pessoais
- **Nome:** Evandro Rhari Limaverde Garcez

## Análise
- **Evento:** Eleições presidenciais em torno do mundo
- **Pergunta central da análise:** Mercados sobre eleições políticas se comportam de forma parecida com mercados esportivos?
- **Hipótese inicial:** Se usarmos as mesmas queries e alertas utilizadas para detectar movimentações atípicas em mercados esportivos, conseguiremos detectar movimentações atípicas em mercados eleitorais.


## Queries
- [Link para o Google Drive](https://drive.google.com/drive/folders/1h5-J3-4RxClTxHFy0S8m2UEvXSRybo3M?usp=sharing)

## Recursos
- **Tabelas ou datasets utilizados no BigQuery:** Foram usados, especialmente, os datasets
  - `polymarket_optimized.markets`
  - `polymarket_optimized.trades`
  - `polymarket_mart.daily_market_stats`
- **Período atualizado:** Todo o período anterior a 25/07/2026

## Pesquisas
A das queries foi detectar amplitudes acima do normal numa dada janela em seu entorno. O primeiro alerta não detectou o desejado, porém, mantendo em mente o problema com o primeiro, o segundo alerta foi bem mais satisfatório.

## Nota pessoal
Estou profundamente insatisfeito com o meu trabalho. Ele é estremamente derivado do trabalho do Carlos Pereira e acredito que as transformações que fiz são menos que insubstanciais: elas degradam o resultado.

Durante o desenvolvimento, me senti incompetente e incapaz. Acredito que, no que diz respeito a banco de dados e BigQuery, tenha aprendido de forma satisfatória, porém não entendo nada de mercado financeiro especulativo e não tenho interesse em nenhum dos assuntos dos mercados do Polymarket, que variam entre política, futebol, guerras e datas. Não sabia sequer que informação poderia tirar desses dados, e por conseguinte não tinha certeza de como. 

Sou entusiastico em aprender novos assuntos, e tentei aprender um pouco sobre mercados financeiros e eleições para realizar a entrega de forma satisfatória. No entanto, o prazo se mostrou muito curto para entregar dois projeto volumosos em conteúdo técnico (esse e o de WebDev) ao mesmo tempo que se educa nos fundamentos da economia especulativa e os diferentes sistemas de eleição através do mundo. Dessa forma, o resultado foi um trabalho plagiado, desinteressante e de baixa qualidade. 

Me sinto envergonhado do meu trabalho e de estar escrevendo essa nota e irei procurar por outros momentos, mais oportunos, para treinar BigQuery.