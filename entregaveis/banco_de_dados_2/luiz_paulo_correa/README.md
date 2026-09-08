# **Entregável Banco de Dados 2**
Luiz Paulo Corrêa da Silva

Análise de mercados do Polymarket usando BigQuery

**OBS:**
Para executar o código, faça o download da pasta do drive localizado em:

https://drive.google.com/drive/folders/1cz4pZrHGCSVgy0nAkbzjnZKcgt1hgC7z?usp=drive_link

e adicione os arquivos na pasta dados. Não coloque a pasta inteira, apenas os arquivos.

# Mercado Escolhido
Em 30 agosto de 2024, a rede social **X** (antigo Twitter) foi bloqueada por determinação judicial do Supremo Tribunal Federal Brasileiro. A partir desse dia, a expectativa para que a rede social voltasse a operar era alta. Nesse sentido, um mercado denominado "Will Brazil unban X before October?" surgiu no Polymarket.

Assim, a seguinte análise apresenta a variação do comportamento do preço das apostas desse mercado no decorrer de setembro. O objetivo principal é criar um script de análise capaz de identificar momentos chaves de virada do mercado, onde fatores externos alteraram bruscamente a precificação do mercado.

Para validação do script, utilizaremos a cronologia de eventos mapeada pela **agênciaBrasil**, podendo ser acessada [nesse link](https://agenciabrasil.ebc.com.br/justica/noticia/2024-10/liberacao-do-x-confira-cronologia-da-suspensao-da-rede-social).

Como exemplo, seguem alguns eventos ocorridos no mês de setembro:
1. 2/9 - A Starlink recorre da decisão que determinou o bloqueio das contas bancárias da empresa. 
2. 13/9 - Moraes determina a transferência de R$ 18,3 milhões que foram bloqueados nas contas da Starlink e da rede social X para a União. A medida serviu para garantir o pagamento das multas.
3. 26/9 - Os advogados do X apresentam os documentos solicitados e pedem o desbloqueio da plataforma.
4. 27/9 - O ministro nega o desbloqueio e faz novas determinações. Moraes pede que a empresa pague a multa de R$ 10 milhões pelo uso do Cloudflare. Além disso, determina que a advogada Rachel Villa Nova pague multa de R$ 300 mil.

Acredito que os eventos ocorridos na data acima tenham causado grande reviravolta no mercado. Testaremos a hipótese com a análise exploratória de dados.

# Tabelas e Datasets Utilizados
As consultas foram executadas no ambiente Google Cloud BigQuery, utilizando a base de dados fornecida.

- `polymarket_optimized.markets` : Utilizada na exploração inicial para validar as datas de abertura (created_at) e fechamento (end_date) do mercado nº 506198.

- `polymarket_mart.daily_market_stats`: Tabela agregada explorada inicialmente, mas descartada. A tabela misturava as apostas do SIM e do NÃO no mesmo registro diário.

- `polymarket_optimized.trades`: A tabela principal utilizada nesta análise. Permitiu o agrupamento agrupamento diário isolando a coluna asset_id (separando o comportamento do token "SIM" do token "NÃO"). A partir desta tabela, extraímos:

    - O Preço Médio Diário (`AVG(price)`);

    - O Volume Financeiro em Dólares (`SUM(usd_amount)`).

# Período Analisado
A análise focou-se no mês de vigência da aposta:

- Data de Início: 30 de Agosto de 2024 (Data do bloqueio do X e abertura do mercado).

- Data de Fim: 30 de Setembro de 2024 (Fim do prazo para a liquidação da aposta "antes de Outubro").

# Alertas Criados para Identificar Momentos Chave
Para automatizar a identificação de "dias anômalos", foi desenvolvida uma consulta unificada no BigQuery (acessível no notebook relatorio.ipynb) utilizand a função de janela LAG(). Temos os dois alertas:

- Alerta de Choque de Preço (Volatilidade): Disparado quando a variação absoluta da probabilidade (price) do token de um dia para o outro foi maior ou igual a 15% (0.15).

- Alerta de Surto de Volume (Financeiro): Disparado quando a injeção de dólares (usd_amount) num token sofreu um aumento de pelo menos 100% em relação ao dia anterior.

A visualização principal do projeto (gerada com Matplotlib) plota o cruzamento das datas dos alertas com as datas das decisões do STF.

# Conclusão

Podemos observar que algumas apostas aparentam estar correlacionadas com os eventos jurídicos mapeados. Entretanto, não é possível indicar o grau da correlação, já que existem muitas variáveis desconhecidas nesse tipo de evento político.

Para evolução desse trabalho, seria interessante agrupar as apostas em intervalos de tempo menores, como, por exemplo, de 12 em 12 horas ou de 6 em 6 horas. Isso aumentaria o número de amostras e tornaria as variações do gráfico mais compreendidas. Um mapeamento de mais eventos impactantes de naturezas distintas com data e **hora** também poderiam ser mais úteis para compreender melhor as variações.
