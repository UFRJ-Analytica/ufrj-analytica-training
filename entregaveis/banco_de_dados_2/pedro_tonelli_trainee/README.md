# Entrega Banco de Dados II — Análise Polymarket no BigQuery

## Trainee
* **Nome:** Pedro Tonelli da Cunha

## Mercado Escolhido
* **Evento / Pergunta:** Will the Sacramento Kings win the NBA Champion?
* **Market ID:** `507892`
* **Dataset / Tabelas Utilizadas:** `even-continuity-441808-j0.polymarket_optimized.trades`

---

## Pergunta Central da Análise
Como o volume de negociação e a probabilidade implícita (preço) do mercado do Sacramento Kings na NBA se comportaram ao longo da temporada, e como picos atípicos de negociação relacionam-se com variações bruscas de preço induzidas por acontecimentos reais da liga?

## Hipótese Inicial
Picos de volume anormalmente altos desviam-se significativamente da média móvel recente (7 dias) e concentram-se em momentos decisivos ou eventos externos relevantes do calendário da NBA, acompanhando ou precedendo altas variações de probabilidade (volatilidade abrupta).

## Período Analisado
Outubro de 2024 a Abril de 2025 (Temporada Regular e Fase Final da NBA).

---

## Cruzamento com Acontecimentos Reais da NBA

Para validar os disparos dos alertas estatísticos no BigQuery, cruzamos os picos de volume e oscilações de preço com as notícias e o calendário oficial da temporada 2024–2025 da NBA:

1. **Outubro / Novembro 2024 (Alta Volatilidade Inicial):**
   * **Fato Real:** A aquisição do astro **DeMar DeRozan** numa troca tripla gerou forte otimismo inicial na torcida e no mercado. 
   * **Impacto no Mercado:** A probabilidade oscilava bruscamente (entre 20% e 90%) à medida que o time emplacava vitórias contra adversários diretos, refletindo a adaptação e a expectativa sobre o novo trio (DeRozan, Fox e Sabonis).

2. **Dezembro 2024 (Pico Recorde de $8,5M em Volume - Alerta Duplo):**
   * **Fato Real:** Ocorreu durante as fases decisivas do **NBA In-Season Tournament (NBA Cup)**.
   * **Impacto no Mercado:** O Kings realizou uma campanha de destaque na fase de grupos e disputou jogos de eliminação direta. Por se tratar de partidas decisivas com grande cobertura midiática, o mercado registrou uma entrada massiva de liquidez especulativa, acionando o Alerta Duplo de Volume e Volatilidade.

3. **Janeiro a Abril 2025 (Queda para ~0% e Estabilização):**
   * **Fato Real:** Sequência de lesões em peças-chave do elenco e a altíssima competitividade da Conferência Oeste empurraram o Kings para a zona do Play-In.
   * **Impacto no Mercado:** O mercado precificou a perda de desempenho e a baixa probabilidade de um título real, fazendo a probabilidade despencar para perto de 0% e o volume de negociação secar na reta final.

---

## Resumo das Consultas e Alertas Desenvolvidos
1. **Exploração Inicial:** Mapeamento dos principais mercados no Polymarket por volume para seleção do estudo de caso.
2. **Consolidação Diária e Alertas em SQL (70+ linhas):**
   * **Alerta 1 (Pico de Volume Anormal):** Identifica dias em que o volume negociado superou a média móvel dos 7 dias anteriores em mais de 2 desvios padrões ($Volume > Média_{7d} + 2 \times STD_{7d}$).
   * **Alerta 2 (Volatilidade Abrupta de Preço):** Sinaliza dias em que a variação absoluta da probabilidade (preço médio `YES`) foi igual ou superior a 5% em 24 horas ($\Delta Preço \ge 0.05$).

## Link dos Dados no Google Drive
Os dados brutos e agregados exportados do BigQuery utilizados nesta análise estão disponíveis na pasta pública:
* [Link para a Pasta de Dados no Google Drive](https://drive.google.com/drive/folders/1W0xtGu6tKcgyKUPRcE8FpFzAsCUu9cRJ?usp=sharing)