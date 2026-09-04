import pandas as pd
import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go

def request(endpoint, method="GET", p=None, body=None):
    resposta = requests.request(url=f"http://127.0.0.1:8000/julio_machado{endpoint}",
                                params=p, method=method, json=body)
    if resposta.status_code == 200:
        dados = resposta.json()
        if method.upper() == "GET":
            df = pd.DataFrame(dados)
            return df
        return dados
    else:
        st.error("Não foi possível executar a operação")


st.header("Dados Básicos e Análises")

st.subheader("KPIs")
resumo = request("/estatisticas/resumo")

dados = resumo.iloc[0]
c1, c2, c3, c4 = st.columns(4)

c1.metric(
        label="Total de Municípios", 
        value=f"{dados['total_municipios']:,}".replace(",", ".")
    )
c2.metric(
        label="Total de Estados", 
        value=dados['total_estados']
    )

c3.metric(
        label="Ano Referência", 
        value=dados['ano_referencia']
    )
c4.metric(
        label="Mais Populoso", 
        value=dados['municipio_mais_populoso']
    )

st.metric(
        label="População Total", 
        value=f"{dados['populacao_total_brasil']:,}".replace(",", ".")
    )

st.divider()

st.subheader("Estados")

estados = request("/estados")
st.dataframe(estados, hide_index=True)

st.divider()

st.subheader("Municipios")

nome = st.text_input("Digite um nome")
id_uf = st.text_input("Digite o id do estado") 
limite = st.number_input("Digite um limite",step=1)
params1 = {}
if nome.strip():
    params1["nome"] = nome.strip()

if id_uf.strip():
    params1["id_uf"] = id_uf.strip()

if limite:
    params1["limit"] = limite

municipios = request("/municipios", p = params1 if params1 else None)
if municipios is not None and not municipios.empty:
    st.dataframe(municipios, hide_index=True)
else:
    st.warning("Nenhum dado encontrado para gerar a tabela.")

st.divider()

st.subheader("Top Municípios Mais Populosos")

params2 = {}
limite2 = st.number_input("Digite um limite",step=1, key="limit")
if limite2:
    params2["limit"] = limite2
top_mun = request("/populacao/top-municipios", p = params2 if params2 else None)
if top_mun is not None and not top_mun.empty:
    st.dataframe(top_mun, hide_index=True)
    fig = px.bar(
        top_mun, 
        x="nome_municipio", 
        y="populacao",
        labels={"nome_municipio": "Município", "populacao": "População"}
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para gerar o gráfico.")

st.divider()

st.subheader("População por Região")
popreg = request("/populacao/por-regiao")
if popreg is not None and not popreg.empty:
    fig = px.pie(
            popreg,
            names="nome_regiao",
            values="populacao",
            hole=0.2,
        )

    fig.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>População: %{value:,.0f}<extra></extra>",
        )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para gerar o gráfico.")

st.divider()

st.subheader("População por estado")

filtro = {}
params3 = st.number_input("Digite um id de região",step=1, key="regiao")
if params3:
    filtro["id_regiao"] = params3
popest = request("/populacao/por-uf", p = filtro if filtro else None)
if popest is not None and not popest.empty:
    fig = px.bar(
            popest,
            x="sigla_uf",
            y="populacao",  
            hover_name="nome_uf",
            labels={"sigla_uf": "Estado", "populacao": "População"},
            color="populacao",
            color_continuous_scale="Viridis",
        )

    
    fig.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="outside",
        )

    fig.update_layout(
            xaxis_title="Estado",
            yaxis_title="População",
            coloraxis_showscale=False,  
            height=600,
        )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para gerar o gráfico.")

st.divider()

st.subheader("Distribuição da População")

dist = request("/populacao/distribuicao")
if dist is not None and not dist.empty:
    df_long = dist.melt(var_name="Porte", value_name="Quantidade")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_long["Porte"],
            y=df_long["Quantidade"],
            name="Municípios",
            text=df_long["Quantidade"],
            textposition="outside",
            marker_color=["#7ec8ff", "#0068c9", "#ffb3b3"] # Cores similares às da imagem
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_long["Porte"],
            y=df_long["Quantidade"],
            mode="lines",
            name="Curva de Distribuição",
            line=dict(
                color="#f1f389", 
                width=3, 
                shape="linear"
            )
        )
    )


    fig.update_layout(
        xaxis_title="Porte",
        yaxis_title="Nº de Municípios",
        showlegend=False,
        bargap=0.05,  
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para gerar o gráfico.")

st.divider()

st.subheader("Dispersão de Municípios por Estado e População por Estado, por Região")

disp = request("/populacao/dispersao-uf")
if disp is not None and not disp.empty:
    fig = px.scatter(
        disp,
        x="total_municipios",     
        y="populacao_media",      
        color="nome_regiao",      
        hover_name="sigla_uf",    
        labels={
            "total_municipios": "Total de Municípios",
            "populacao_media": "População Média",
            "nome_regiao": "Região"
        }
    )

    fig.update_traces(
        marker=dict(size=12, opacity=0.8, line=dict(width=1, color='DarkSlateGrey'))
    )

    fig.update_layout(
        xaxis_title="Total de Municípios no Estado",
        yaxis_title="População Média",
        height=550,
        legend_title_text="Região"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado retornado para gerar o gráfico.")

st.divider()
st.subheader("Mapa de calor: Região x Porte")

heatmap = request("/populacao/heatmap-regiao-porte")

df_matriz = heatmap.set_index("nome_regiao")[["PEQUENO", "MEDIO", "GRANDE"]]

valor_min = df_matriz.values.min()
valor_max = df_matriz.values.max()
df_matriz_norm = (df_matriz - valor_min) / (valor_max - valor_min)

fig = px.imshow(
    df_matriz_norm,
    labels=dict(x="Porte do Município", y="Região", color="Escala Normalizada"),
    x=df_matriz_norm.columns,
    y=df_matriz_norm.index,
    text_auto=False,
    aspect="auto",
    color_continuous_scale="Reds"
)

fig.update_traces(
    text=df_matriz.values, 
    texttemplate="%{text}"
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Quantidade de Municípios por Região")

df_tabela = heatmap[["nome_regiao", "total_municipios"]]

st.dataframe(
    df_tabela,
    column_config={
        "nome_regiao": "Região",
        "total_municipios": "Total de Municípios"
    },
    hide_index=True,
    use_container_width=True
)

st.divider()

st.subheader("Gerenciamento de Municípios")
st.divider()
st.subheader("Criar Município")
with st.form(key="form_novo_municipio", clear_on_submit=True):
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome_municipio = st.text_input("Nome do Município", placeholder="Ex: Rio de Janeiro")
        id_uf = st.number_input("ID da UF (Estado)", min_value=1, step=1)
        
    with col2:
        valor = st.number_input("População", min_value=0, step=1)
        unidade = st.text_input("Unidade", value="pessoas", placeholder="Ex: pessoas")
        
    # Botão de envio
    submit_button = st.form_submit_button(label="Adicionar Município")

if submit_button:
    if not nome_municipio or not unidade:
        st.warning("Por favor, preencha todos os campos de texto antes de enviar.")
    else:
        payload = {
            "nome_municipio": nome_municipio,
            "id_uf": id_uf,
            "valor": valor,
            "unidade": unidade
        }
        
        with st.spinner("Salvando no banco de dados..."):
            resultado = request("/municipios", method="POST", body=payload)
        
        if resultado:
            st.success("Município cadastrado com sucesso!")
            st.subheader("Dados inseridos:")
            st.table(resultado)
        else:
            st.error("Erro ao cadastrar. Verifique os dados ou a conexão com a API.")

st.divider()

st.subheader("Deletar Município")


with st.form(key="form_excluir_municipio"):
    id_municipio = st.number_input("ID do Município a ser excluído", min_value=1, step=1)
    
    btn_excluir = st.form_submit_button("Excluir Município", type="primary")

if btn_excluir:
    with st.spinner("Apagando registros no banco de dados..."):
        
        endpoint_dinamico = f"/municipios/{id_municipio}"
        
        resultado = request(endpoint_dinamico, method="DELETE")
        
        if resultado is not None:
            st.success(f" Município de ID {id_municipio} excluído com sucesso!")

st.divider()

st.subheader("Consultar Detalhes do Município")

with st.form(key="form_busca_municipio"):
    id_input = st.number_input("ID do Município", min_value=1, step=1)
    btn_consultar = st.form_submit_button("Buscar Município")

if btn_consultar:
    with st.spinner("Buscando dados no banco..."):
        
        ep = f"/municipios/{id_input}"
        
        detalhes = request(ep)
        
        if detalhes is not None and not detalhes.empty:
            st.success("Dados encontrados com sucesso!")
            info = detalhes.iloc[0]
            
            st.subheader(f"📍 {info['nome_municipio']} - {info['sigla_uf']}")
            col2, col3 = st.columns(2)
            col2.metric("Estado", info['nome_uf'])
            
            populacao_formatada = f"{info['valor']:,}".replace(",", ".")
            col3.metric("População", f"{populacao_formatada} {info['unidade']}")
            
            st.divider()
            
            st.markdown("**Tabela de Dados Completos:**")
            st.dataframe(detalhes, hide_index=True, use_container_width=True)
            
        else:
            st.warning(f"Nenhum município encontrado com o ID {id_input}.")

st.divider()

st.subheader("Atualizar informações do município")
with st.form(key="form_atualizar_municipio"):
    
    id_municipio = st.number_input("ID do Município a ser atualizado", min_value=1, step=1, help="Digite o ID exato do município")
    
    st.divider()
    st.markdown("### Novos Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome_municipio = st.text_input("Novo Nome do Município", placeholder="Ex: Niterói")
        id_uf = st.number_input("Novo ID da UF", min_value=1, step=1)
        
    with col2:
        valor = st.number_input("Nova População (Valor)", min_value=0, step=1)
        unidade = st.text_input("Nova Unidade", value="pessoas", placeholder="Ex: pessoas")
        
    btn_atualizar = st.form_submit_button("Salvar Alterações", type="primary")

if btn_atualizar:
    if not nome_municipio or not unidade:
        st.warning("Por favor, preencha o nome do município e a unidade.")
    else:

        payload = {
            "nome_municipio": nome_municipio,
            "id_uf": id_uf,
            "valor": valor,
            "unidade": unidade
        }
        
        with st.spinner("Atualizando registros no banco de dados..."):
            endpoint_dinamico = f"/municipios/{id_municipio}"
            
            resultado = request(endpoint_dinamico, method="PUT", body=payload)
            

            if resultado is not None:
                st.success(f"Município (ID: {id_municipio}) atualizado com sucesso!")
                
                st.subheader("Dados Atualizados:")
                st.table(resultado)

st.title("Gestão de Registros (Cadastro)")

tab1, tab2, tab3, tab4 = st.tabs([
    "Criar", 
    "Deletar", 
    "Listar", 
    "Atualizar"
])

with tab1:
    st.subheader("Criar Novo Registro")
    with st.form("form_criar"):
        id_mun_criar = st.number_input("ID do Município", min_value=1, step=1)
        status = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluído"])
        prioridade = st.slider("Prioridade", 1, 5, 3)
        descricao = st.text_area("Descrição")
        
        btn_criar = st.form_submit_button("Criar Registro")

    if btn_criar:
        payload2 = {}
        payload2 = {"status": status, "prioridade": prioridade, "descricao": descricao}
        resultado = request(f"/municipios/{id_mun_criar}/registros", method="POST", body=payload2)
        if resultado:
            st.success("Registro criado com sucesso!")
            st.json(resultado)

with tab2:
    st.subheader("Deletar Registro")
    with st.form("form_deletar"):
        id_reg_del = st.number_input("ID do Registro para deletar", min_value=1, step=1)
        btn_deletar = st.form_submit_button("Excluir Registro", type="primary")

    if btn_deletar:
        resultado = request(f"/registros/{id_reg_del}", method="DELETE")
        if resultado is not None:
            st.success(f"Registro {id_reg_del} deletado.")

with tab3:
    st.subheader("Listar Registros por Município")
    id_mun_listar = st.number_input("ID do Município para listar", min_value=1, step=1, key="listar")
    btn_listar = st.button("Buscar Registros")

    if btn_listar:
        resultado = request(f"/municipios/{id_mun_listar}/registros", method="GET")
        if resultado is not None and not resultado.empty:
            st.dataframe(resultado, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro encontrado para este município.")

with tab4:
    st.subheader("Atualizar Registro")
    with st.form("form_atualizar"):
        id_reg_update = st.number_input("ID do Registro para atualizar", min_value=1, step=1)
        id_mun_new = st.number_input("Novo ID do Município (opcional)", min_value=0, step=1, help="Deixe 0 se não quiser alterar")
        
        status_up = st.selectbox("Novo Status", [None, "Pendente", "Em Andamento", "Concluído"], index=0)
        prioridade_up = st.number_input("Nova Prioridade", min_value=0, max_value=5, value=0, help="0 para não alterar")
        descricao_up = st.text_area("Nova Descrição (vazio para não alterar)")
        
        btn_update = st.form_submit_button("Atualizar Registro")

    if btn_update:
        payload3 = {}
        if id_mun_new > 0: payload3["id_municipio"] = id_mun_new
        if status_up: payload3["status"] = status_up
        if prioridade_up > 0: payload3["prioridade"] = prioridade_up
        if descricao_up: payload3["descricao"] = descricao_up
        
        resultado = request(f"/registros/{id_reg_update}", method="PUT", body=payload3)
        if resultado:
            st.success("Registro atualizado!")
            st.json(resultado)