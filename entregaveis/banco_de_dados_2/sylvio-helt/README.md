# Banco de Dados II 


**Trainee:** Sylvio Helt

**Mercado analisado:** “TikTok banned in the US before May 2025?” | ID: `507276`


## Pergunta central

Como o volume negociado e a probabilidade implícita do resultado `Yes` se comportaram ao longo do mercado, especialmente em períodos próximos a acontecimentos políticos, jurídicos e operacionais relacionados à possível proibição do TikTok nos Estados Unidos?

## Hipótese inicial

A hipótese inicial é que a divulgação de informações relevantes esteja temporalmente associada ao aumento da atividade de negociação e a mudanças mais intensas na probabilidade atribuída pelos participantes do mercado.

A análise busca observar essas relações temporais sem assumir que os acontecimentos externos sejam, isoladamente, a causa direta das movimentações identificadas.

## Período analisado

Os registros de negociação analisados compreendem o período entre:

* **Primeira negociação:** 18 de setembro de 2024;
* **Última negociação:** 21 de janeiro de 2025.

O período entre 17 e 21 de janeiro de 2025 recebeu atenção especial por concentrar acontecimentos externos relevantes e uma parcela significativa da atividade do mercado.

## Dados utilizados

As consultas foram executadas no projeto:

```text
even-continuity-441808-j0
```

Foram utilizadas as seguintes tabelas e views:

```text
polymarket_optimized.markets
polymarket_optimized.trades
polymarket_mart.v_market_daily
```

A tabela `markets` foi utilizada para selecionar e caracterizar o mercado. A tabela `trades` forneceu os registros individuais de negociação utilizados nas análises horárias e na construção dos alertas. A view `v_market_daily` foi utilizada na exploração inicial do comportamento diário do mercado.

## Descrição dos alertas

### `alerta_volume`

Consulta responsável por identificar horas com volume negociado anormalmente elevado.

O alerta compara o volume atual com as 24 horas anteriores e é disparado quando:

```text
Z-score do volume > 3
Volume horário > US$ 100.000
```

A consulta final identificou 11 alertas de volume. Entre eles, 7 ocorreram dentro da janela de seis horas antes ou depois dos eventos externos selecionados, resultando em uma correspondência temporal de 63,64%.

### `alerta_preco`

Consulta responsável por identificar movimentações atípicas na probabilidade implícita do resultado `Yes`.

O alerta compara a variação absoluta do preço com as 24 horas anteriores e é disparado quando:

```text
Z-score da variação > 4
Variação absoluta >= 0,05
```

A consulta final identificou 32 alertas de preço. Entre eles, 3 ocorreram dentro da janela definida em relação aos eventos externos, resultando em uma correspondência temporal de 9,38%.

## Principais resultados

O alerta de volume apresentou maior correspondência temporal com os quatro acontecimentos externos selecionados. Isso indica que aumentos anormais na atividade de negociação ocorreram frequentemente próximos à divulgação de informações relevantes.

O alerta de preço apresentou menor correspondência com esses acontecimentos. Esse indicador funcionou como uma medida mais ampla de instabilidade do mercado, podendo capturar revisões de expectativa, movimentos especulativos, alterações de liquidez e outras dinâmicas não associadas diretamente aos eventos selecionados.

As taxas representam correspondência temporal dentro da janela adotada e não demonstram uma relação causal entre as notícias e os movimentos observados.

## Arquivos CSV

A pasta pública contendo os arquivos CSV utilizados na análise está disponível em:

**[Dados](https://drive.google.com/drive/folders/1GTV_L_Gp7OphdyrxM-KJs9paRv9C8tM8?usp=drive_link)**