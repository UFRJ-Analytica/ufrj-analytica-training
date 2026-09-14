
# imagem com python ja instalado (slim p nao ter coisa a mais)
FROM python:3.11-slim

#definir a pasta de trabalho dentro do conteiner (onde os comandos vao operar, evitar jogar arquivos soltos na raiz)
WORKDIR /app

# copia requirements.txt, se esse arquivo nao mudar, docker aproveita e nao reinstala tudo a cada build
COPY requirements.txt . 
# obs COPY segue a estrutura: COPY <origem no computador> <destino no container>

# instala o que ta listado no requeirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copia o frontend
COPY app.py .
COPY pages/ ./pages
COPY data/ ./data/

# 8501 é a porta padrão do streamlit, é só pra documentar que essa á a porta
EXPOSE 8501

# comando que vai iniciar o app quando o container sobe
# --server.address=0.0.0.0 é importanye: sem isso, o Streamlit só aceita conexões de dentro do próprio container, e não daria p acessar
# pelo navegador do Windows/WSL2
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
# streamlit por padrao escuta so em localhost dentro do container, que é inacessivel de fora

# obs rodar "docker build -t analytica-frontend ." com o dokcer desktop aberto........