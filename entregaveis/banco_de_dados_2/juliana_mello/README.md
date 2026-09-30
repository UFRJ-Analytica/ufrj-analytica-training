# Banco de Dados II — Entrega: Polymarket no BigQuery

**Trainee:** Juliana

## Evento escolhido

**Super Bowl LX: Seattle Seahawks vs. New England Patriots** (08/02/2026, Levi's Stadium, Santa Clara).

- Confronto decidido em **25/01/2026** (Championship Sunday): Patriots bateram os Broncos (10-7) na AFC
  Championship à tarde e foram considerados favoritos ao título por algumas horas, já que ainda não se
  sabia contra quem jogariam; à noite, os Seahawks bateram os Rams (31-27) na NFC Championship e viraram
  favoritos do jogo até o kickoff.
- Resultado: **Seattle Seahawks venceram por 29-13**.

## Achado real da exploração (Q1) que molda a análise

A tabela `markets` revela três famílias de mercado para este tema, só a primeira é usada como fonte
principal:

1. Mercado de confronto direto: `event_title = 'Seattle vs. New England'`, `question = 'Seahawks
   vs. Patriots'`. Um único `market_id`, criado em **26/01/2026 03:19 UTC** (depois que os dois jogos de
   conferência já tinham terminado), `end_date` em 08/02/2026 23:30 UTC (horário do kickoff), volume ≈
   US$ 36,3M. **Fonte das Etapas 3 a 5, 7 e 8.**
2. Mercado de futuros da temporada: `event_title = 'Big Game Champion 2026'`, um `market_id` por
   time (32 times), aberto desde abril/2025. Como o mercado de confronto direto só existe a partir de
   26/01, a troca de favorito relatada pela imprensa em 25/01 só é observável aqui, nos mercados
   isolados de Seahawks e Patriots. **Fonte só da Etapa 6a.**
3. Mercados da temporada passada (`event_title = 'Super Bowl Champion 2025'` e `'Super Bowl LIX
   Winner'`, referentes ao Super Bowl LIX de fev/2025): aparecem na Q1 só porque o filtro por nome de
   time bate com qualquer temporada.

## Pergunta central

A probabilidade implícita do favorito (Seahawks) sofreu reviravolta abrupta durante a semana do jogo,
seja pela troca de favorito nas primeiras horas de 25/01/2026 (só visível nos mercados de futuros), seja
por relatórios de lesão, análises especializadas ou vazamentos de escalação perto do kickoff, ou o
mercado apenas convergiu de forma gradual, com a volatilidade caindo antes do fechamento?

## Hipótese inicial

Uma vez definido o confronto, o mercado converge para o favorito (Seahawks) e a volatilidade cai de
forma acentuada nos dias finais antes do kickoff. A hipótese não presume qual notícia específica
"causou" um eventual salto — apenas testa se existem saltos localizáveis (com destaque para o salto já
documentado de 25/01) e se o padrão de convergência/queda de volatilidade se confirma no restante da
semana.

## Tabelas e datasets utilizados no BigQuery

- `even-continuity-441808-j0.polymarket_optimized.markets` — metadados dos market_id envolvidos.
- `even-continuity-441808-j0.polymarket_mart.v_market_daily` — série diária agregada, usada para o
  mercado de confronto direto (Etapas 3 a 5, Alerta 1).
- `even-continuity-441808-j0.polymarket_optimized.trades` — negociações individuais, particionada por
  dia e clusterizada por `market_id`, usada em duas janelas curtas: 25/01–26/01 (mercados de futuros,
  reversão pré-confronto) e 01/02–08/02 (mercado de confronto direto, semana do jogo).

## Período analisado

- Reversão pré-confronto (só nos futuros): 25/01/2026 a 26/01/2026.
- Janela principal (mercado de confronto direto): 26/01/2026 (abertura) a 08/02/2026 (kickoff).
- Baseline de volatilidade: 26/01/2026 a 29/01/2026.
- Janela crítica do Alerta 2 (confronto direto): 01/02/2026 a 08/02/2026.
- Liquidação: dados de 09/02/2026 em diante são pós-resolução e são excluídos das análises de
  tendência; o `end_date` do mercado (08/02 23:30 UTC) coincide com o kickoff, não com o fim do jogo, o
  que é registrado como limitação (ver abaixo).

## Consciência de custo no BigQuery (cota de 1 TB)

- `markets` é pequena e não-particionada: os filtros pontuais da Etapa 1/2 custam poucos MB.
- Etapas 3 a 5 e o Alerta 1 usam só `polymarket_mart.v_market_daily`, filtrando um único `market_id`(custo desprezível).
- Só a Etapa 6 e o Alerta 2 tocam `polymarket_optimized.trades`, e mesmo assim restritas a no máximo 3
  `market_id` e no máximo 10 dias no total, usando poda de partição via `OR`/`IN` em vez de um `BETWEEN`
  largo que leria dias irrelevantes (30/01–31/01).
- Nenhuma query usa `SELECT *`; todas selecionam só as colunas necessárias.
- Antes de rodar qualquer query pela primeira vez, use a estimativa de bytes do BigQuery Studio — para
  as consultas deste roteiro, o esperado é a faixa de dezenas/centenas de MB, nunca GB.

## Descrição dos arquivos SQL e do alerta final

O `relatorio.ipynb` contém, na ordem:

1. Exploração inicial (já realizada) — descoberta das três famílias de mercado e confirmação de que o
   confronto direto é um único `market_id`.
2. Confirmação dos três `market_id` necessários (confronto direto + 2 futuros) e verificação de qual
   time o preço do confronto direto representa (checando se o último preço converge para perto de 1,
   compatível com a vitória dos Seahawks).
3. Série diária do mercado de confronto direto.
4. Métrica de confiança implícita (`|preço - 0,5| × 2`), substituindo a métrica de "participação de
   volume entre candidatos" usada em cenários multi-outcome, já que aqui há um único mercado.
5. Métrica de volatilidade (desvio padrão móvel de 2 dias).
6. Zoom horário em duas fontes: mercados de futuros em 25/01–26/01 (reversão pré-confronto) e mercado
   de confronto direto em 01/02–08/02 (semana do jogo).
7. **Alerta 1 — `ALERTA_CONCENTRACAO`**: dias com confiança implícita acima de 0,50 e volatilidade
   abaixo de 50% da baseline.
8. **Alerta 2 — `ALERTA_REVIRAVOLTA`**: saltos horários de PMPV >= 0,05, combinando via `UNION ALL` os
   sinais dos futuros (25/01) e do confronto direto (semana do jogo).
9. Visualização dos dois alertas e métricas de assertividade (fração de disparos na semana do jogo;
   fração de saltos horários coerentes com o resultado final).

## Resumo do resultado final

**Hipótese original:** próximo à cerimônia/jogo, o mercado concentra volume e probabilidade no
favorito, com a volatilidade caindo nos dias finais; testamos também se havia reviravolta abrupta por
notícia/crítica/vazamento perto do fechamento.

**Resultado: a hipótese não se confirmou como formulada, mas revelou um padrão mais interessante.**

- **Concentração** — não cresceu perto do jogo. O `ALERTA_CONCENTRACAO` (limiar relativo, top 30% da
  distribuição de confiança implícita do próprio mercado) disparou em só 2 dias (28/01 e 04/02),
  espalhados, sem tendência de alta sustentada. A confiança média até caiu levemente na semana do jogo
  (0,09 → 0,08).
- **Volatilidade** — maior nos dias finais (0,0376) do que na baseline pós-abertura (0,0338), o oposto
  do previsto. O padrão real foi calmaria na véspera seguida de disparo no próprio dia do jogo,
  coincidindo com a explosão de volume.
- **Reviravolta** — o `ALERTA_REVIRAVOLTA` encontrou 4 sinais horários, todos concentrados em 25-26/01
  (não na semana do jogo). Eles reconstroem, com dados de mercado, a sequência real dos jogos de
  conferência: Patriots sobem (+0,095) ao vencerem a AFC Championship; Seahawks sobem em 3 passos
  (+0,098, +0,116, +0,084) ao longo da vitória na NFC Championship. Nenhum sinal disparou na semana do
  Super Bowl em si (maior variação horária: 0,013, bem abaixo do limiar de 0,05).

**Conclusão:** a parte específica da hipótese ("reviravolta perto do fechamento por crítica ou
vazamento") não se sustenta neste mercado. Mas o princípio mais geral por trás dela, que o mercado
reage de forma abrupta a informação nova e relevante, se confirma com clareza, só que no momento
errado da linha do tempo em relação ao previsto: no resultado real dos jogos eliminatórios de
conferência (25-26/01), não em uma notícia de bastidor perto do jogo final.

## Link do Google Drive com os CSVs

[https://drive.google.com/drive/folders/1dufJYqHRwq-Xr1yZC95fNTBoGzvHTsgE?usp=drive_link]

## Limitações conhecidas

- Um salto de preço horário não comprova, por si só, que uma crítica específica ou um vazamento causou
  aquele movimento — pode refletir apenas rebalanceamento de posições ou baixa liquidez pontual.
- A reversão de 25/01 é o único salto com causa pública amplamente documentada; qualquer outro salto
  identificado na semana do jogo deve ser cruzado, por proximidade temporal (não causalidade), com
  notícias reais daquela janela.
- O `end_date` do mercado de confronto direto (08/02 23:30 UTC) coincide com o horário do kickoff, não
  com o fim da partida — é possível que tenham ocorrido negociações relevantes depois desse timestamp,
  já durante o jogo; esta análise foca exclusivamente no período pré-jogo.
- A leitura de qual time o preço do mercado de confronto direto representa foi inferida (checando se o
  preço final converge para perto de 1, dado que os Seahawks venceram) — não confirmada diretamente por
  uma coluna de schema; se o BigQuery expuser uma coluna explícita de outcome/token, prefira usá-la.
