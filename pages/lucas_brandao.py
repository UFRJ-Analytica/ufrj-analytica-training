import streamlit as st
import requests

st.set_page_config(page_title="Painel do Lucas", layout="wide")

st.title("Painel Populacional - Lucas Brandão")
st.write("Visão geral dos dados populacionais dos municípios brasileiros.")
st.divider()

st.subheader("Indicadores Principais (KPIs)")

# Requisição para a nova rota de KPIs
url_kpis = "http://127.0.0.1:8000/lucas-brandao/kpis"

try:
    resposta = requests.get(url_kpis)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        
        #Cria 4 colunas na tela para colocar os indicadores lado a lado
        col1, col2, col3, col4 = st.columns(4)
        
        #Formatação de número para ficar com separador de milhar (ex: 200.000.000)
        populacao_formatada = f"{dados['populacao_total']:,}".replace(",", ".")
        populoso_formatado = f"{dados['populacao_mais_populoso']:,}".replace(",", ".")
        
        #Exibindo as métricas
        col1.metric("Total de Municípios", dados['total_municipios'])
        col2.metric("Total de Estados", dados['total_estados'])
        col3.metric("População Nacional", populacao_formatada)
        col4.metric(f"Mais Populoso ({dados['nome_mais_populoso']})", populoso_formatado)
        
    else:
        st.error(f"Erro ao carregar os dados. Código: {resposta.status_code}")
except requests.exceptions.ConnectionError:
    st.error("A API está fora do ar. Verifique o terminal do Backend.")