import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# configuração 
API_URL = "http://127.0.0.1:8000/luiz-paulo"
PALETA_REGIOES = px.colors.qualitative.Set2
ALTURA_GRAFICO = 400

st.set_page_config(page_title="Acompanhamento Populacional", layout="wide")


# get generico da api
def chamar_api(caminho: str, params: dict | None = None) -> list | dict | None:
    try:
        resposta = requests.get(f"{API_URL}{caminho}", params=params, timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        st.error(
            "não foi possível se comunicar com o servidor."
        )
        return None

#post/put/delete generico da api
def enviar_api(metodo: str, caminho: str, dados: dict | None = None) -> requests.Response | None:
    try:
        return requests.request(metodo, f"{API_URL}{caminho}", json=dados, timeout=5)
    except requests.exceptions.RequestException:
        st.error("não foi possível se comunicar com o servidor")
        return None


def tratar_resposta(resp: requests.Response | None, mensagem_sucesso: str) -> bool:
    """mostra sucesso ou erro pro usuário. Devolve True se deu certo."""
    if resp is None:
        return False
    if 200 <= resp.status_code < 300:
        st.success(mensagem_sucesso)
        return True
    try:
        detalhe = resp.json().get("detail", "erro desconhecido")
    except ValueError:
        detalhe = "erro desconhecido"
    st.error(detalhe)
    return False

# busca de dados na apii
def buscar_kpis() -> dict | None:
    return chamar_api("/estatisticas/resumo")

def buscar_top_municipios(limit: int) -> list | None:
    return chamar_api("/populacao/top-municipios", params={"limit": limit})

def buscar_populacao_por_regiao() -> list | None:
    return chamar_api("/populacao/por-regiao")

def buscar_populacao_por_uf(id_regiao: int | None) -> list | None:
    params = {"id_regiao": id_regiao} if id_regiao else None
    return chamar_api("/populacao/por-uf", params=params)

def buscar_distribuicao() -> list | None:
    return chamar_api("/populacao/distribuicao")

def buscar_dispersao() -> list | None:
    return chamar_api("/populacao/dispersao-uf")

def buscar_heatmap() -> list | None:
    return chamar_api("/populacao/heatmap-regiao-porte")

def buscar_regioes() -> list | None:
    return chamar_api("/regioes")

def buscar_estados() -> list | None:
    return chamar_api("/estados")

def buscar_municipios() -> list | None:
    return chamar_api("/municipios")

def buscar_municipio(id_municipio: int) -> dict | None:
    return chamar_api(f"/municipios/{id_municipio}")

def buscar_registros(id_municipio: int) -> list | None:
    return chamar_api(f"/municipios/{id_municipio}/registros")

# renderização dos graficos
def renderizar_kpis(kpis: dict) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Municípios", kpis["total_municipios"])
    col2.metric("Estados", kpis["total_estados"])
    col3.metric("População do Brasil", f"{kpis['populacao_total']:,.0f}")
    col4.metric("Ano de referência", kpis["ano_referencia"])
    col5.metric(
        "Mais populoso",
        f"{kpis['municipio_mais_populoso']}"
    )


def renderizar_top_municipios() -> None:
    limite = st.slider("Quantos municípios mostrar?", 5, 50, 10)
    dados = buscar_top_municipios(limite)
    if not dados:
        return
    df = pd.DataFrame(dados)
    st.dataframe(df, hide_index=True, use_container_width=True)
    fig = px.bar(df, x="nome_municipio", y="valor", title="Municípios mais populosos", height=ALTURA_GRAFICO)
    st.plotly_chart(fig, use_container_width=True)


def renderizar_populacao_por_regiao() -> None:
    dados = buscar_populacao_por_regiao()
    if not dados:
        return
    df = pd.DataFrame(dados)
    fig = px.pie(
        df, names="nome_regiao", values="populacao", title="População por região",
        color_discrete_sequence=PALETA_REGIOES, height=ALTURA_GRAFICO,
    )
    st.plotly_chart(fig, use_container_width=True)


def renderizar_populacao_por_uf() -> None:
    regioes = buscar_regioes() or []
    opcoes = {"Todas": None} | {r["nome_regiao"]: r["id_regiao"] for r in regioes}
    escolha = st.selectbox("Filtrar por região", opcoes.keys())
    dados = buscar_populacao_por_uf(opcoes[escolha])
    if not dados:
        return
    df = pd.DataFrame(dados)
    fig = px.bar(df, x="sigla_uf", y="populacao", title="População por estado", height=ALTURA_GRAFICO)
    st.plotly_chart(fig, use_container_width=True)


def renderizar_distribuicao() -> None:
    dados = buscar_distribuicao()
    if not dados:
        return
    df = pd.DataFrame(dados)
    fig = px.histogram(df, x="valor", title="Distribuição da população dos municípios", height=ALTURA_GRAFICO)
    st.plotly_chart(fig, use_container_width=True)


def renderizar_dispersao() -> None:
    dados = buscar_dispersao()
    if not dados:
        return
    df = pd.DataFrame(dados)
    fig = px.scatter(
        df, x="qtd_municipios", y="populacao_media", color="nome_regiao", hover_name="nome_uf",
        title="Municípios x população média por estado",
        color_discrete_sequence=PALETA_REGIOES, height=ALTURA_GRAFICO,
    )
    st.plotly_chart(fig, use_container_width=True)


def renderizar_heatmap() -> None:
    dados = buscar_heatmap()
    if not dados:
        return
    df = pd.DataFrame(dados)
    matriz = df.pivot(index="nome_regiao", columns="porte", values="quantidade").fillna(0)
    fig = px.imshow(matriz, text_auto=True, title="Região x porte do município", height=ALTURA_GRAFICO)
    st.plotly_chart(fig, use_container_width=True)

# renderização dos forms
def renderizar_form_criar_municipio() -> None:
    estados = buscar_estados() or []
    opcoes_estado = {e["nome_uf"]: e["id_uf"] for e in estados}

    with st.form("form_criar_municipio", clear_on_submit=True):
        st.subheader("Cadastrar município novo")
        nome = st.text_input("Nome do município")
        estado_escolhido = st.selectbox("Estado", opcoes_estado.keys())
        populacao = st.number_input("População", min_value=0, step=1)
        if st.form_submit_button("Cadastrar"):
            resp = enviar_api("POST", "/municipios", {
                "nome_municipio": nome,
                "id_uf": opcoes_estado[estado_escolhido],
                "populacao": populacao,
            })
            if tratar_resposta(resp, "Município criado!"):
                st.rerun()


def renderizar_form_editar_municipio() -> None:
    municipios = buscar_municipios() or []
    if not municipios:
        st.info("Nenhum município cadastrado ainda.")
        return

    st.subheader("Editar ou remover município existente")
    opcoes_municipio = {f"{m['nome_municipio']} ({m['id_municipio']})": m["id_municipio"] for m in municipios}
    escolha = st.selectbox("Município", opcoes_municipio.keys(), key="editar_municipio_select")
    id_escolhido = opcoes_municipio[escolha]
    atual = buscar_municipio(id_escolhido)
    if atual is None:
        return

    estados = buscar_estados() or []
    opcoes_estado = {e["nome_uf"]: e["id_uf"] for e in estados}
    nomes_estado = list(opcoes_estado.keys())
    ids_estado = list(opcoes_estado.values())
    indice_atual = ids_estado.index(atual["id_uf"]) if atual["id_uf"] in ids_estado else 0

    with st.form("form_editar_municipio"):
        nome = st.text_input("Nome", value=atual["nome_municipio"])
        estado_escolhido = st.selectbox("Estado", nomes_estado, index=indice_atual)
        col_salvar, col_remover = st.columns(2)
        salvar = col_salvar.form_submit_button("Salvar alterações")
        remover = col_remover.form_submit_button("Remover município")

    if salvar:
        resp = enviar_api("PUT", f"/municipios/{id_escolhido}", {
            "nome_municipio": nome,
            "id_uf": opcoes_estado[estado_escolhido],
        })
        if tratar_resposta(resp, "Município atualizado!"):
            st.rerun()

    if remover:
        resp = enviar_api("DELETE", f"/municipios/{id_escolhido}")
        if tratar_resposta(resp, "Município removido!"):
            st.rerun()


def renderizar_registros_gestor() -> None:
    municipios = buscar_municipios() or []
    if not municipios:
        st.info("Cadastre um município primeiro.")
        return

    st.subheader("Anotações do gestor")
    opcoes_municipio = {f"{m['nome_municipio']} ({m['id_municipio']})": m["id_municipio"] for m in municipios}
    escolha = st.selectbox("Município", opcoes_municipio.keys(), key="registros_municipio_select")
    id_municipio = opcoes_municipio[escolha]

    registros = buscar_registros(id_municipio) or []
    for r in registros:
        titulo = f"{r['status'] or '(sem status)'} — {r['prioridade'] or '(sem prioridade)'}"
        with st.expander(titulo):
            st.write(r["observacao"] or "(sem observação)")
            st.caption(f"Responsável: {r['responsavel'] or '—'} | Criado em: {r['data_registro']}")
            if st.button("Remover anotação", key=f"remover_registro_{r['id_registro']}"):
                resp = enviar_api("DELETE", f"/registros/{r['id_registro']}")
                if tratar_resposta(resp, "Anotação removida!"):
                    st.rerun()

    with st.form("form_nova_anotacao", clear_on_submit=True):
        st.write("Nova anotação")
        status = st.text_input("Status")
        prioridade = st.text_input("Prioridade")
        observacao = st.text_area("Observação")
        responsavel = st.text_input("Responsável")
        if st.form_submit_button("Adicionar"):
            resp = enviar_api("POST", f"/municipios/{id_municipio}/registros", {
                "status": status or None,
                "prioridade": prioridade or None,
                "observacao": observacao or None,
                "responsavel": responsavel or None,
            })
            if tratar_resposta(resp, "Anotação adicionada!"):
                st.rerun()


# layout das areas da pagina
def renderizar_area_analise() -> None:
    kpis = buscar_kpis()
    if kpis:
        renderizar_kpis(kpis)

    aba_geral, aba_estados, aba_avancado = st.tabs(["Visão geral", "Por estado", "Avançado"])
    with aba_geral:
        renderizar_top_municipios()
        renderizar_populacao_por_regiao()
    with aba_estados:
        renderizar_populacao_por_uf()
        renderizar_distribuicao()
    with aba_avancado:
        renderizar_dispersao()
        renderizar_heatmap()


def renderizar_area_cadastro() -> None:
    aba_municipio, aba_registros = st.tabs(["Município", "Anotações"])
    with aba_municipio:
        renderizar_form_criar_municipio()
        st.divider()
        renderizar_form_editar_municipio()
    with aba_registros:
        renderizar_registros_gestor()


st.title("Acompanhamento Populacional")

aba_analise, aba_cadastro = st.tabs(["Análise", "Cadastro"])
with aba_analise:
    renderizar_area_analise()
with aba_cadastro:
    renderizar_area_cadastro()
