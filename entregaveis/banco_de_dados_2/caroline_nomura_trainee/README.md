## Trainee

Caroline Yumi Nomura

## Evento escolhido: Vencedor do oscar de melhor filme em 2025

A 97ª edição do Oscar ocorreu em 2 de março de 2025, com o vencedor do prêmio de melhor filme sendo Anora, dirigido por Sean Baker, que concorreu com fortes produções como O Brutalista, Conclave, Emilia Pérez e Ainda Estou Aqui.

## Pergunta central

Como o mercado de apostas foi influenciado por vitórias em premiações preliminares e a polêmicas relacionadas aos filmes concorrentes?

## Hipótese inicial

Consideramos duas circunstâncias externas relevantes que culminaram para o desfecho deste mercado:

* Polêmicas envolvendo a atriz de um dos filmes: Em 31 de janeiro, a atriz espanhola Karla Sofía Gascón, estrela de Emilia Pérez, esteve no centro de polêmicas nas redes sociais. A hipótese é de que esse evento gerou um sell-off (queda abrupta na probabilidade do filme por pânico dos investidores), provocando uma migração em massa de liquidez para seu principal concorrente (Anora).
* Vitórias importantes de um filme em premiações anteriores: Anora ganhou as principais categorias em três grandes premiações preliminares: o Critics Choice Awards (07/Fev) e, mais criticamente, os prêmios do Sindicato dos Produtores (PGA) e Sindicato dos Diretores (DGA) no mesmo fim de semana (09/Fev). Supõe-se que o mercado antecipou e reagiu a essas vitórias com picos extremos de volume e ajustes bruscos de probabilidade a favor de Anora.

## Período analisado

20 de janeiro de 2025 a 05 de março de 2025.

## Tabelas e datasets utilizados 

Os dados foram extraídos do dataset otimizado do Polymarket (`polymarket_optimized`):

* `markets` (Tabela de Dimensão): Utilizada na etapa exploratória para descobrir o `market_id` dos eventos em que cada filme competidor ganha o prêmio, interpretar os metadados do evento e entender a mecânica de encerramento do mercado.

* `trades` (Tabela de Fato): A base principal do projeto. Contém o histórico granular transacional, permitindo a extração do volume financeiro (`usd_amount`), o preço/probabilidade de fechamento (`price`) e a direção da agressão ao mercado (`taker_direction`), essencial para calcular a pressão de compra vs. venda.

## Estrutura das consultas (Pipeline SQL)

O pipeline de processamento de dados foi construído de forma modular e está separado em blocos de código no notebook (`relatorio.ipynb`) com as devidas descrições, demonstrando embaixo de cada query a sua tabela CSV resultante. As consultas foram estruturadas para isolar o ruído do mercado e destacar anomalias reais, divididas em duas etapas principais:

1. Blocos de exploração e tendências: Consultas iniciais focadas na tabela de dimensões e na camada Mart. Elas filtram os IDs dos mercados, realizam agregações diárias para evitar o alto custo computacional e extraem métricas básicas de oscilação e liquidez na visão macro para entender a trajetória dos filmes da categoria.

2. Bloco dos alertas: Uma consulta analítica complexa baseada em CTEs e window functions que atua como um radar de anomalias operacionais na tabela de fatos. A query implementa duas regras estatísticas ao mesmo tempo:

* Alerta de liquidez (z-score): Dispara quando o volume financeiro horário ultrapassa 2.5 desvios padrão acima da média móvel das últimas 72 horas.

* Alerta de momentum: Dispara quando há um salto absoluto na probabilidade de fechamento ≥ 15% em um intervalo de 24 horas.

* Enriquecimento estratégico: O alerta também calcula a fatia de volume originada por agressores de compra (`Taker = BUY`), classificando o evento dinamicamente como "Pressão crítica de compra" ou "Pressão crítica de venda".

## Link da pasta do Google Drive com os arquivos CSV

https://drive.google.com/drive/folders/1ywfu01DfSv60sYkHdKyG2hAcj6IHXO0A?usp=sharing