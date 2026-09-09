import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards #deixa + bonito
import pandas as pd
import numpy as np
import plotly.express as px
import requests

st.set_page_config(page_title="Painel Populacional",page_icon="📊",layout="wide")

st.title("📊 Sistema para Análise Populacional")
st.caption("Dashboard utilizando FastAPI + Streamlit")


URL_API="http://127.0.0.1:8000/rebecca_simao"


def buscar(endpoint):
    try:
        resposta=requests.get(f"{URL_API}/{endpoint}",timeout=5)
    except requests.exceptions.RequestException:
        st.error("A API está fora do ar. Confira se o Uvicorn está rodando.")
        st.stop()

    if resposta.status_code==200:return resposta.json()
    st.error(f"Erro {resposta.status_code}: {resposta.text}")
    st.stop()


def enviar(metodo,endpoint,parametros=None):
    try:
        resposta=requests.request(metodo,f"{URL_API}/{endpoint}",params=parametros,timeout=5)
    except requests.exceptions.RequestException:
        st.error("A API está fora do ar. Confira se o Uvicorn está rodando.")
        return False

    if 200<=resposta.status_code<300:
        return True

    try:
        erro=resposta.json()["detail"]
    except:
        erro=resposta.text

    st.error(f"Erro {resposta.status_code}: {erro}")
    return False




dados=buscar("kpi")
st.subheader("Indicadores Gerais")

c1,c2,c3,c4=st.columns(4)
c1.metric("🌎 Regiões",dados["total_regioes"])
c2.metric("🏛 Estados",dados["total_estados"])
c3.metric("🏘 Municípios",dados["total_municipios"])
c4.metric("👥 População",f'{dados["total_populacao"]:,.0f}'.replace(",", "."))

style_metric_cards(background_color="#FFFFFF",border_left_color="#4F8BF9",border_size_px=1)

esq,dir=st.columns([2,1])
with esq:
    with st.container(border=True):
        st.subheader("Município mais populoso")
        st.metric(dados["municipio mais populoso"]["nome_municipio"],f'{dados["municipio mais populoso"]["valor"]:,.0f}'.replace(",","."))
        st.caption(f"Ano de referência: {dados['ano']}")
        st.caption(f"Fonte: {dados['fonte']}")
with dir:
    with st.container(border=True):
        st.subheader("Resumo")
        st.write(f"**Regiões:** {dados['total_regioes']}")
        st.write(f"**Estados:** {dados['total_estados']}")
        st.write(f"**Municípios:** {dados['total_municipios']}")

st.divider()
st.header("📈 Explorar Dados")

aba1,aba2,aba3,aba4,aba5,aba6=st.tabs(["🏆 Ranking","Regiões","Estados","Histograma","Dispersão","Heatmap"])

with aba1:
    quant=st.slider("Quantidade de municípios",3,20,10)
    ranking=buscar(f"ranking_popu_muni?quant={quant}")
    df=pd.DataFrame(ranking["Top municipio"])
    fig=px.bar(df,x="nome_municipio",y="valor",text_auto=True,title=f"Top {quant} municípios mais populosos")
    fig.update_layout(xaxis_title="",yaxis_title="População")
    st.plotly_chart(fig,use_container_width=True)

    tabela=df.rename(columns={"nome_municipio":"Município","valor":"População"})
    tabela["População"]=tabela["População"].map(lambda x:f"{x:,.0f}".replace(",","."))
    st.dataframe(tabela,use_container_width=True,hide_index=True)


with aba2:
    regiao=buscar("popu_regiao")
    df=pd.DataFrame(regiao["Top regiao"])
    fig=px.pie(df,names="nome_regiao",values="SUM(popu.valor)",hole=.55,title="População por região")
    fig.update_traces(textposition="inside",textinfo="percent+label")
    st.plotly_chart(fig,use_container_width=True)


with aba3:
    filtro=st.selectbox("Filtrar região",["Todas","Norte","Nordeste","Centro-Oeste","Sudeste","Sul"])
    if filtro=="Todas":
        estados=buscar("popu_estados")
    else:
        estados=buscar(f"popu_estados?nome_regiao={filtro}")

    df=pd.DataFrame(estados["Estados"])
    fig=px.bar(df,x="nome_uf",y="SUM(popu.valor)",color="SUM(popu.valor)",title="População por Estado")
    fig.update_layout(xaxis_title="",yaxis_title="População")
    st.plotly_chart(fig,use_container_width=True)

    st.dataframe(df,use_container_width=True,hide_index=True)


with aba4:
    dados=buscar("distribuicao_populacao")
    df=pd.DataFrame(dados)
    df["populacao_log"]=np.log10(df["valor"])
    fig=px.histogram(df,x="populacao_log",nbins=35,title="Distribuição da população dos municípios")

    fig.update_layout(xaxis_title="População",yaxis_title="Quantidade de municípios")
    fig.update_xaxes(tickvals=[3,4,5,6,7],ticktext=["1 mil","10 mil","100 mil","1 milhão","10 milhões"])
    st.plotly_chart(fig,use_container_width=True)

with aba5:
    dados=buscar("dispersao")
    df=pd.DataFrame(dados)
    fig=px.scatter(df,x="qntMunicipios",y="popu_media",color="nome_regiao",hover_name="nome_uf",log_y=True,title="Quantidade de municípios x População média por estado")
    fig.update_layout(xaxis_title="Quantidade de municípios",yaxis_title="População média")   

    st.plotly_chart(fig,use_container_width=True)
    tabela=df.rename(columns={"nome_uf":"Estado","nome_regiao":"Região","qntMunicipios":"Municípios","popu_media":"População média"})
    tabela["População média"]=tabela["População média"].map(lambda x:f"{x:,.0f}".replace(",","."))
    st.dataframe(tabela,use_container_width=True,hide_index=True)

with aba6:
    dados=buscar("heatMap")
    df=pd.DataFrame(dados)
    matriz=df.pivot(index="nome_regiao",columns="porte",values="qntMunicipios")
    matriz=matriz[["Pequeno","Medio","Grande"]]
    ordem_regioes=["Norte","Nordeste","Centro-Oeste","Sudeste","Sul"]
    matriz=matriz.reindex(ordem_regioes)

    fig=px.imshow(matriz,text_auto=True,title="Quantidade de municípios por porte")
    fig.update_layout(xaxis_title="Porte do município",yaxis_title="Região")
    st.plotly_chart(fig,use_container_width=True)
    tabela=df.rename(columns={"nome_regiao":"Região","porte":"Porte","qntMunicipios":"Municípios"})
    st.dataframe(tabela,use_container_width=True,hide_index=True)



st.divider()
st.header("📝 Cadastros")

if "mensagem" in st.session_state:
    st.success(st.session_state["mensagem"])
    del st.session_state["mensagem"]

lista_municipios=buscar("municipios")
df_municipios=pd.DataFrame(lista_municipios)
nomes_municipios={}
for municipio in lista_municipios:
    nomes_municipios[municipio["id_municipio"]]=f'{municipio["nome_municipio"]} - {municipio["nome_uf"]}'
ids_municipios=list(nomes_municipios.keys())

if "id_uf" not in df_municipios.columns:
    st.error("Não foi possível carregar os dados dos estados.")
    st.stop()

estados=df_municipios[["id_uf","nome_uf"]].drop_duplicates().sort_values("nome_uf")
nomes_estados=dict(zip(estados["id_uf"],estados["nome_uf"]))
ids_estados=list(nomes_estados.keys())

cad1,cad2=st.tabs(["🏙 Município","📌 Acompanhamento do gestor"])


with cad1:
    novo,consultar,editar=st.tabs(["Cadastrar novo","Consultar","Editar ou remover"])

    with novo:
        st.subheader("Cadastrar município")

        with st.form("novo_municipio"):
            nome_municipio=st.text_input("Nome do município")
            id_uf=st.selectbox("Estado",ids_estados,format_func=lambda x:nomes_estados[x])
            valor=st.number_input("População",min_value=0,step=1)
            ano=st.number_input("Ano",min_value=1900,max_value=2100,value=2025,step=1)
            indicador=st.text_input("Indicador",value="População")
            unidade=st.text_input("Unidade",value="habitantes")
            fonte=st.text_input("Fonte",value="Cadastro manual")

            cadastrar=st.form_submit_button("Cadastrar município",type="primary")

        if cadastrar:
            if nome_municipio.strip()=="":
                st.warning("Informe o nome do município.")
            else:
                parametros={"nome_municipio":nome_municipio,"id_uf":int(id_uf),"ano":int(ano),
                            "indicador":indicador,"valor":int(valor),"unidade":unidade,"fonte":fonte}
                if enviar("POST","municipios/ibge",parametros):
                    st.session_state["mensagem"]="Município cadastrado com sucesso."
                    st.rerun()

    with consultar:
        st.subheader("Consultar município")
        id_consulta=st.selectbox(            "Escolha o município",ids_municipios,format_func=lambda x:nomes_municipios[x],key="consultar_municipio")

        if st.button("Consultar dados"):
            registro=buscar(f"municipios/{id_consulta}/ibge")
            municipio=registro["municipio"]
            populacao=registro["populacao"]

            st.write(f"**Município:** {municipio['nome_municipio']}")
            st.write(f"**ID:** {municipio['id_municipio']}")
            st.write(f"**Estado:** {nomes_estados[municipio['id_uf']]}")
            st.subheader("Dados populacionais")
            df_populacao=pd.DataFrame(populacao)

            if len(df_populacao)>0:
                st.dataframe( df_populacao,use_container_width=True,hide_index=True)
            else:
                st.info("Não há dados populacionais cadastrados para este município.")


    with editar:
        st.subheader("Editar município")
        id_municipio=st.selectbox("Escolha o município",ids_municipios, format_func=lambda x:nomes_municipios[x],key="editar_municipio")
        registro=buscar(f"municipios/{id_municipio}/ibge")
        municipio=registro["municipio"]
        populacao=registro["populacao"]
        if len(populacao)>0:
            pop=populacao[0]
        else:
            pop={"ano":2025,"indicador":"População","valor":0,"unidade":"","fonte":""}

        with st.form("editar_municipio_form"):
            nome_editado=st.text_input("Nome",value=municipio["nome_municipio"])
            id_uf_editado=st.selectbox(
                "Estado",ids_estados,index=ids_estados.index(municipio["id_uf"]),
                format_func=lambda x:nomes_estados[x])
            valor_editado=st.number_input("População",min_value=0,value=int(pop["valor"]),step=1)
            ano_editado=st.number_input("Ano",min_value=1900,max_value=2100,value=int(pop["ano"]),step=1)
            indicador_editado=st.text_input("Indicador",value=pop["indicador"] or "")
            unidade_editada=st.text_input("Unidade",value=pop["unidade"] or "")
            fonte_editada=st.text_input("Fonte",value=pop["fonte"] or "")
            salvar=st.form_submit_button("Salvar alterações",type="primary")

        if salvar:
            parametros={"nome_municipio":nome_editado,"id_uf":int(id_uf_editado),"ano":int(ano_editado),"indicador":indicador_editado,"valor":int(valor_editado),"unidade":unidade_editada,"fonte":fonte_editada}

            if enviar("PATCH",f"municipios/{id_municipio}/ibge",parametros):
                st.session_state["mensagem"]="Município atualizado com sucesso."
                st.rerun()

        st.divider()
        confirmar=st.checkbox("Confirmo que quero remover este município")

        if st.button("Remover município",disabled=not confirmar):
            if enviar("DELETE",f"municipios/{id_municipio}/ibge"):
                st.session_state["mensagem"]="Município removido com sucesso."
                st.rerun()


with cad2:
    st.subheader("Acompanhamento do gestor")

    id_municipio_gestor=st.selectbox("Escolha o município",ids_municipios,format_func=lambda x:nomes_municipios[x], key="municipio_gestor")
    registros=buscar(f"municipios/{id_municipio_gestor}/registros")
    if len(registros)==0:
        st.info("Este município ainda não possui registro de acompanhamento.")
        with st.form("novo_registro_gestor"):
            prioridade=st.text_input("Prioridade",value="Média")
            status=st.text_input("Status",value="Em acompanhamento")
            responsavel=st.text_input("Responsável")
            obs=st.text_area("Observação")
            cadastrar_registro=st.form_submit_button("Adicionar registro",type="primary")

        if cadastrar_registro:
            parametros={"prioridade":prioridade,"status":status,"obs":obs,"responsavel":responsavel}
            if enviar("POST",f"municipios/{id_municipio_gestor}/registros",parametros):
                st.session_state["mensagem"]="Registro criado com sucesso."
                st.rerun()

    else:
        st.write("Registro atual")
        tabela_registros=pd.DataFrame(registros)
        tabela_registros=tabela_registros.rename(columns={"prioridade":"Prioridade","status":"Status",
                                                          "obs":"Observação","responsavel":"Responsável"})
        colunas=["Prioridade","Status","Observação","Responsável"]
        st.dataframe(tabela_registros[colunas],use_container_width=True,hide_index=True)
        registro_atual=registros[0]

        with st.form("editar_registro_gestor"):
            prioridade_editada=st.text_input("Prioridade",value=registro_atual["prioridade"] or "")
            status_editado=st.text_input("Status",value=registro_atual["status"] or "")
            responsavel_editado=st.text_input("Responsável",value=registro_atual["responsavel"] or "")
            obs_editada=st.text_area("Observação",value=registro_atual["obs"] or "")
            salvar_registro=st.form_submit_button("Salvar acompanhamento",type="primary")

        if salvar_registro:
            parametros={"prioridade":prioridade_editada,"status":status_editado,"obs":obs_editada,"responsavel":responsavel_editado}
            if enviar("PATCH",f"municipios/{id_municipio_gestor}/registros",parametros):
                st.session_state["mensagem"]="Registro atualizado com sucesso."
                st.rerun()

        confirmar_registro=st.checkbox("Confirmo que quero remover o registro de acompanhamento")
        if st.button("Remover registro",disabled=not confirmar_registro):
            if enviar("DELETE",f"municipios/{id_municipio_gestor}/registros"):
                st.session_state["mensagem"]="Município removido com sucesso."
                st.rerun()