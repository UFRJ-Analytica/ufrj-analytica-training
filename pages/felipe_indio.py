import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestão Populacional", layout="wide")
st.title("📊 Painel de Acompanhamento Populacional")

API_URL = "http://127.0.0.1:8000/felipe-indio"

def fetch_data(endpoint, params=None):
    try:
        resp = requests.get(f"{API_URL}{endpoint}", params=params)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return None

def post_data(endpoint, data):
    return requests.post(f"{API_URL}{endpoint}", json=data)

def put_data(endpoint, data):
    return requests.put(f"{API_URL}{endpoint}", json=data)

def delete_data(endpoint):
    return requests.delete(f"{API_URL}{endpoint}")

tab_analise, tab_municipios, tab_registros = st.tabs(["📈 Análise de Dados", "🏙️ Gestão de Municípios", "📝 Cadastros do Gestor"])

# ABA 1: ANÁLISE E GRÁFICOS
with tab_analise:
    st.header("Resumo Estatístico")
    resumo = fetch_data("/estatisticas/resumo")
    if resumo:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("População Total", f"{resumo['populacao_total']:,}".replace(",", "."))
        c2.metric("Total de Municípios", resumo['total_municipios'])
        c3.metric("Total de Estados", resumo['total_estados'])
        c4.metric("Mais Populoso", resumo['municipio_mais_populoso'])

    st.divider()
    
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("População por Região")
        dados_regiao = fetch_data("/populacao/por-regiao")
        if dados_regiao:
            fig = px.pie(pd.DataFrame(dados_regiao), names='nome_regiao', values='populacao_total', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    with col_graf2:
        st.subheader("Top N Municípios")
        limite = st.slider("Quantidade (N):", 5, 50, 10)
        dados_top = fetch_data("/populacao/top-municipios", {"limit": limite})
        if dados_top:
            fig2 = px.bar(pd.DataFrame(dados_top), x='nome_municipio', y='populacao', color='sigla_uf')
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Dispersão: Municípios vs População Média por Estado")
    dados_disp = fetch_data("/populacao/dispersao-uf")
    if dados_disp:
        df_disp = pd.DataFrame(dados_disp)
        fig3 = px.scatter(df_disp, x='qtd_municipios', y='media_populacao', color='id_regiao', text='sigla_uf', size='media_populacao')
        fig3.update_traces(textposition='top center')
        st.plotly_chart(fig3, use_container_width=True)


# ABA 2: CRUD DE MUNICÍPIOS
with tab_municipios:
    st.header("Gerenciar Municípios")
    estados = fetch_data("/estados") or []
    opcoes_estados = {e["nome_uf"]: e["id_uf"] for e in estados}

    col_add, col_edit = st.columns(2)
    
    with col_add:
        st.subheader("Adicionar Novo")
        with st.form("form_add_mun"):
            novo_nome = st.text_input("Nome do Município")
            novo_uf = st.selectbox("Estado", options=list(opcoes_estados.keys()))
            nova_pop = st.number_input("População Inicial", min_value=1, step=1)
            submit_add = st.form_submit_button("Criar Município")
            
            if submit_add:
                payload = {"nome_municipio": novo_nome, "id_uf": opcoes_estados[novo_uf], "populacao_inicial": nova_pop}
                res = post_data("/municipios", payload)
                if res.status_code == 201:
                    st.success("Município criado!")
                else:
                    st.error("Erro ao criar.")

    with col_edit:
        st.subheader("Remover Município")
        busca_mun = st.text_input("Buscar por nome para deletar:")
        if busca_mun:
            muns_encontrados = fetch_data("/municipios", {"nome": busca_mun, "limit": 5})
            if muns_encontrados:
                mun_selecionado = st.selectbox("Selecione para excluir:", options=muns_encontrados, format_func=lambda x: x["nome_municipio"])
                if st.button("Deletar"):
                    res = delete_data(f"/municipios/{mun_selecionado['id_municipio']}")
                    if res.status_code == 200:
                        st.success("Removido com sucesso!")
                    else:
                        st.error("Erro ao remover.")

# ABA 3: CADASTRO DO GESTOR
with tab_registros:
    st.header("Anotações e Registros")
    busca_reg = st.text_input("Buscar município por nome (para adicionar/ver registro):")
    
    if busca_reg:
        lista_muns = fetch_data("/municipios", {"nome": busca_reg, "limit": 5})
        if lista_muns:
            mun_alvo = st.selectbox("Selecione o Município:", options=lista_muns, format_func=lambda x: x["nome_municipio"])
            id_alvo = mun_alvo["id_municipio"]
            
            with st.expander("Adicionar Novo Registro", expanded=False):
                with st.form("form_reg"):
                    status = st.selectbox("Status", ["Ativo", "Em Observação", "Crítico"])
                    prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
                    resp = st.text_input("Responsável")
                    obs = st.text_area("Observação")
                    if st.form_submit_button("Salvar Registro"):
                        payload_reg = {"status": status, "prioridade": prioridade, "responsavel": resp, "observacao": obs}
                        post_data(f"/municipios/{id_alvo}/registros", payload_reg)
                        st.success("Salvo!")
            
            st.subheader("Registros Atuais")
            registros = fetch_data(f"/municipios/{id_alvo}/registros")
            if registros:
                for reg in registros:
                    with st.container(border=True):
                        st.markdown(f"**Status:** {reg['status']} | **Prioridade:** {reg['prioridade']}")
                        st.write(f"**Obs:** {reg['observacao']}")
                        st.caption(f"Responsável: {reg['responsavel']} | ID Registro: {reg['id_registro']}")
                        if st.button("Excluir", key=f"del_{reg['id_registro']}"):
                            delete_data(f"/registros/{reg['id_registro']}")
                            st.rerun()
            else:
                st.info("Nenhum registro para este município.")