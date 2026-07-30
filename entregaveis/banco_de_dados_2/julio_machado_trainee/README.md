Nome: Júlio David Machado
Evento: Movimentaçao nos mercados de: Campeão da NFL em 2025.
Pergunta Central: Como as movimentações se comportam perto da data dos jogos?  
Hipótese Inicial: Após partidas com resultados dominantes (21+ Pontos de diferença) o mercado movimenta um volume maior. 
Tabelas e datasets usados: "polymarket_optimized.markets", "polymarket_mart.v_market_daily"
Período analisado: 11 de Novembro de 2024 até 16 de Fevereiro de 2025.
Drive dos dados: https://drive.google.com/drive/folders/1PWKRu78YnIf71Y-nodWUIX_WkN8ns8MD?usp=sharing
Descrição dos arquivos SQL:
A primeira busca foi exploratória com um nome aleatório de um time da NFL para conhecer o datase.
A segunda busca foi exploratória buscando outras opções de mercados usando de base a primeira busca.
A terceira busca foi para coletar os mercados que vão ter o volume observados.
A quarta, quinta e a sétima busca foi para buscar padrões em dias de jogos.
A sexta busca foi para medir o mercado em uma fase de campeonato inativa, com intenção de criar filtros melhores.
A oitava busca foi o primeiro alerta para movimentações acima do normal nos mercados de Super Bowl 2025 e verificar se houve jogos no dia ou no dia posterior a movimentação.
A nona busca foi o segundo alerta, com intenção de testar movimentações pós-jogos nos próprios mercados, para verificar se existia alguma chance da primeira hipótese ter alguma validade, desconsiderando os mercados de Super Bowl 2025(hipotese totalmente descartada).