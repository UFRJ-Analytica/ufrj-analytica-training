import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


API_URL = "http://127.0.0.1:8000/pedro-ferrari"

st.set_page_config(page_title="Acompanhamento Populacional", layout="wide")

st.title("Sistema de Acompanhamento Populacional")
st.write("Painel para análise e cadastro de informações dos municípios brasileiros.")

try:
    resposta = requests.get(f"{API_URL}/status", timeout=5)
    resposta.raise_for_status()
    st.success("API conectada com sucesso!")
except requests.RequestException:
    st.error("Não foi possível conectar à API. Verifique se o FastAPI está ligado.")
    st.stop()

#evita agora ficar repetindo varias vezes 
def get_api(rota, params=None):
    try:
        resposta = requests.get(
            f"{API_URL}{rota}",
            params=params,
            timeout=5
        )
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException:
        st.error("Não foi possível consultar a API.")
        return []


def mostrar_resultado(resposta, sucesso, erro):
    if resposta.ok:
        st.success(sucesso)
    else:
        st.error(erro)


aba_analise, aba_cadastro = st.tabs(["Análise", "Cadastro"])

with aba_analise:

    st.header("Análise Populacional")
    st.write("Nesta área é possível visualizar os principais indicadores populacionais dos municípios brasileiros.")

    # KPIs
    resumo = get_api("/estatisticas/resumo")
    if resumo:

        col_municipios, col_estados, col_populacao, col_ano = st.columns(4)
        col_municipios.metric("Total de municípios", resumo["total_municipios"])
        col_estados.metric("Total de estados", resumo["total_estados"])
        col_populacao.metric("População total", f"{resumo['populacao_total']:,}".replace(",", "."))
        col_ano.metric("Ano de referência", resumo["ano_referencia"])

        col_municipio_populoso, col_populacao_municipio = st.columns(2)
        col_municipio_populoso.metric("Município mais populoso", resumo["municipio_mais_populoso"])
        col_populacao_municipio.metric("População do município", f"{resumo['populacao_municipio_mais_populoso']:,}".replace(",", "."))
    else: 
        st.warning("Não deu pra carregar os indicadores agora.")

    st.divider()
    st.subheader("Municípios mais populosos")

    quantidade_top = st.sidebar.slider("Quantidade de municípios no ranking", min_value=3, max_value=10, value=5, step=1, key="top_municipios")

    try:
        resposta_top = requests.get(f"{API_URL}/populacao/top-municipios", params={"limit": quantidade_top}, timeout=5)
        resposta_top.raise_for_status()
        df_top = pd.DataFrame(resposta_top.json())

        col_grafico, col_tabela = st.columns([2, 1])

        with col_grafico:
            df_top_grafico = df_top.sort_values(by="populacao")
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.barh(df_top_grafico["nome_municipio"], df_top_grafico["populacao"])
            ax.set_title(f"Top {quantidade_top} municípios mais populosos")
            ax.set_xlabel("População")
            ax.set_ylabel("Município")
            plt.tight_layout()
            st.pyplot(fig, width=700)
            plt.close(fig)

        with col_tabela:
            st.write("Ranking")
            tabela_top = df_top[["nome_municipio", "populacao"]].copy()
            tabela_top.columns = ["Município", "População"]
            st.table(tabela_top)

    except requests.RequestException:
        st.warning("Não foi possível carregar os municípios mais populosos.")

    st.divider()
    st.subheader("População por região")

    try:
        resposta_regioes = requests.get(f"{API_URL}/populacao/por-regiao", timeout=5)
        resposta_regioes.raise_for_status()
        df_regioes = pd.DataFrame(resposta_regioes.json()).sort_values(by="populacao", ascending=False)

        col_grafico_regiao, col_tabela_regiao = st.columns([2, 1])

        with col_grafico_regiao:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(df_regioes["populacao"], labels=df_regioes["nome_regiao"], autopct="%1.1f%%", startangle=90)
            ax.set_title("Distribuição da população brasileira por região")
            ax.axis("equal")
            st.pyplot(fig, width=700)
            plt.close(fig)

        with col_tabela_regiao:
            st.write("População total")
            st.dataframe(df_regioes, hide_index=True, use_container_width=True)

    except requests.RequestException:
        st.warning("Não foi possível carregar a população por região.")

    st.divider()
    st.subheader("População por estado")

    try:
        # precisa das regiões pra montar o filtro do gráfico
        regioes = get_api("/regioes")
        opcoes_regioes = {"Todas as regiões": None}
        for regiao in regioes:
            opcoes_regioes[regiao["nome_regiao"]] = regiao["id_regiao"]

        regiao_escolhida = st.sidebar.selectbox("Região para comparar os estados", opcoes_regioes.keys(), key="filtro_regiao_estados")
        id_regiao = opcoes_regioes[regiao_escolhida]
        parametros = {"id_regiao": id_regiao} if id_regiao is not None else {}

        resposta_estados = requests.get(f"{API_URL}/populacao/por-uf", params=parametros, timeout=5)
        resposta_estados.raise_for_status()
        df_estados = pd.DataFrame(resposta_estados.json()).sort_values(by="populacao_total")

        fig, ax = plt.subplots(figsize=(8, 7))
        ax.barh(df_estados["sigla_uf"], df_estados["populacao_total"])
        ax.set_title(f"População dos estados — {regiao_escolhida}")
        ax.set_xlabel("População")
        ax.set_ylabel("Estado")
        plt.tight_layout()
        st.pyplot(fig, width=700)
        plt.close(fig)

    except requests.RequestException:
        st.warning("Não foi possível carregar a população por estado.")

    st.divider()
    st.subheader("Distribuição da população dos municípios")

    try:
        resposta_distribuicao = requests.get(f"{API_URL}/populacao/distribuicao", timeout=5)
        resposta_distribuicao.raise_for_status()
        df_distribuicao = pd.DataFrame(resposta_distribuicao.json())
        populacoes = df_distribuicao.loc[df_distribuicao["populacao"] > 0, "populacao"]

        # escala log porque a maioria dos municípios é pequena e uns poucos são gigantes
        faixas = np.logspace(np.log10(populacoes.min()), np.log10(populacoes.max()), 20)

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.hist(populacoes, bins=faixas, edgecolor="black")
        ax.set_xscale("log")
        ax.set_title("Distribuição da população entre os municípios brasileiros")
        ax.set_xlabel("População")
        ax.set_ylabel("Quantidade de municípios")
        plt.tight_layout()
        st.pyplot(fig, width=700)
        plt.close(fig)

        st.write(f"Total de municípios analisados: {len(df_distribuicao)}")

    except requests.RequestException:
        st.warning("Não foi possível carregar a distribuição populacional.")

    st.divider()
    st.subheader("Municípios e população média por estado")

    try:
        resposta_dispersao = requests.get(f"{API_URL}/populacao/dispersao-uf", timeout=5)
        resposta_dispersao.raise_for_status()
        df_dispersao = pd.DataFrame(resposta_dispersao.json())

        fig, ax = plt.subplots(figsize=(9, 5))

        for nome_regiao, dados_regiao in df_dispersao.groupby("nome_regiao"):
            ax.scatter(dados_regiao["quantidade_municipios"], dados_regiao["populacao_media"], label=nome_regiao, s=70)

        for _, estado in df_dispersao.iterrows():
            ax.annotate(estado["sigla_uf"], (estado["quantidade_municipios"], estado["populacao_media"]), xytext=(4, 4), textcoords="offset points", fontsize=8)

        ax.set_title("Quantidade de municípios x população média por estado")
        ax.set_xlabel("Quantidade de municípios")
        ax.set_ylabel("População média")
        ax.ticklabel_format(style="plain", axis="y")
        ax.legend(title="Região")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, width=700)
        plt.close(fig)

    except requests.RequestException:
        st.warning("Não foi possível carregar o gráfico de dispersão.")

    st.divider()
    st.subheader("Quantidade de municípios por região e porte")

    try:
        resposta_heatmap = requests.get(f"{API_URL}/populacao/heatmap-regiao-porte", timeout=5)
        resposta_heatmap.raise_for_status()
        df_heatmap = pd.DataFrame(resposta_heatmap.json())

        tabela_heatmap = df_heatmap.pivot(index="nome_regiao", columns="porte", values="quantidade_municipios").fillna(0)
        tabela_heatmap = tabela_heatmap.reindex(columns=["Pequeno", "Médio", "Grande"], fill_value=0)

        fig, ax = plt.subplots(figsize=(7, 4))
        imagem = ax.imshow(tabela_heatmap.values, aspect="auto", cmap="Blues")
        ax.set_xticks(range(len(tabela_heatmap.columns)))
        ax.set_xticklabels(tabela_heatmap.columns)
        ax.set_yticks(range(len(tabela_heatmap.index)))
        ax.set_yticklabels(tabela_heatmap.index)

        for linha in range(len(tabela_heatmap.index)):
            for coluna in range(len(tabela_heatmap.columns)):
                valor = int(tabela_heatmap.iloc[linha, coluna])
                ax.text(coluna, linha, valor, ha="center", va="center")

        ax.set_title("Quantidade de municípios por região e porte")
        ax.set_xlabel("Porte do município")
        ax.set_ylabel("Região")
        fig.colorbar(imagem, ax=ax, label="Quantidade de municípios")
        plt.tight_layout()
        st.pyplot(fig, width=700)
        plt.close(fig)

    except requests.RequestException:
        st.warning("Não foi possível carregar o mapa de calor.")


with aba_cadastro:

    st.header("Área de cadastro")
    st.write("Cadastre municípios e informações de acompanhamento.")

    aba_municipios, aba_registros = st.tabs(["Municípios", "Registros do gestor"])

    estados = get_api("/estados")
    opcoes_estados = {f"{estado['nome_uf']} ({estado['sigla_uf']})": estado["id_uf"] for estado in estados}

    # ---------- municípios ----------
    with aba_municipios:

        st.subheader("Cadastrar município")

        if not opcoes_estados:
            st.warning("Não foi possível carregar os estados.")
        else:
            with st.form("criar_municipio"):
                nome = st.text_input("Nome do município", key="nome_novo_municipio")
                estado = st.selectbox("Estado", list(opcoes_estados.keys()), key="estado_novo_municipio")
                populacao = st.number_input("População inicial", min_value=0, step=1, key="populacao_novo_municipio")
                cadastrar = st.form_submit_button("Cadastrar município")

            if cadastrar:
                if not nome.strip():
                    st.warning("Informe o nome do município.")
                else:
                    dados = {
                        "nome_municipio": nome,
                        "id_uf": opcoes_estados[estado],
                        "populacao_inicial": int(populacao),
                    }
                    resposta = requests.post(f"{API_URL}/municipios", json=dados, timeout=5)
                    mostrar_resultado(resposta, "Município cadastrado com sucesso!", "Não foi possível cadastrar o município.")

        st.divider()
        st.subheader("Editar ou remover município")

        busca = st.text_input("Buscar município pelo nome", key="busca_editar_municipio")
        parametros = {"limit": 50}
        if busca.strip():
            parametros["nome"] = busca.strip()

        municipios = get_api("/municipios", parametros)

        if municipios:
            opcoes_municipios = {
                f"{municipio['nome_municipio']} - ID {municipio['id_municipio']}": municipio["id_municipio"]
                for municipio in municipios
            }
            municipio_selecionado = st.selectbox("Selecione o município", list(opcoes_municipios.keys()), key="municipio_selecionado_edicao")
            id_municipio = opcoes_municipios[municipio_selecionado]

            detalhe = get_api(f"/municipios/{id_municipio}")

            if detalhe and opcoes_estados:
                nomes_estados = list(opcoes_estados.keys())
                ids_estados = list(opcoes_estados.values())
                indice_estado = ids_estados.index(detalhe["id_uf"]) if detalhe["id_uf"] in ids_estados else 0

                with st.form(f"editar_municipio_{id_municipio}"):
                    novo_nome = st.text_input("Nome do município", value=detalhe["nome_municipio"], key=f"nome_municipio_{id_municipio}")
                    novo_estado = st.selectbox("Estado", nomes_estados, index=indice_estado, key=f"estado_municipio_{id_municipio}")
                    nova_populacao = st.number_input("População", min_value=0, value=int(detalhe.get("populacao") or 0), step=1, key=f"populacao_municipio_{id_municipio}")
                    atualizar = st.form_submit_button("Atualizar município")

                if atualizar:
                    dados = {
                        "nome_municipio": novo_nome,
                        "id_uf": opcoes_estados[novo_estado],
                        "populacao_inicial": int(nova_populacao),
                    }
                    resposta = requests.put(f"{API_URL}/municipios/{id_municipio}", json=dados, timeout=5)
                    mostrar_resultado(resposta, "Município atualizado com sucesso!", "Não foi possível atualizar o município.")

                if st.button("Remover município", key=f"remover_municipio_{id_municipio}"):
                    resposta = requests.delete(f"{API_URL}/municipios/{id_municipio}", timeout=5)
                    mostrar_resultado(resposta, "Município removido com sucesso!", "Não foi possível remover o município.")

        else:
            st.info("Nenhum município encontrado.")

    # ---------- registros do gestor ----------
    with aba_registros:

        st.subheader("Registros de acompanhamento")

        busca_registro = st.text_input("Buscar município", key="busca_municipio_registro")
        parametros = {"limit": 50}
        if busca_registro.strip():
            parametros["nome"] = busca_registro.strip()

        municipios = get_api("/municipios", parametros)

        if municipios:
            opcoes_municipios = {
                f"{municipio['nome_municipio']} - ID {municipio['id_municipio']}": municipio["id_municipio"]
                for municipio in municipios
            }
            municipio_selecionado = st.selectbox("Selecione o município", list(opcoes_municipios.keys()), key="municipio_selecionado_registro")
            id_municipio = opcoes_municipios[municipio_selecionado]

            registros = get_api(f"/municipios/{id_municipio}/registros")

            st.write("Registros cadastrados")

            if registros:
                df_registros = pd.DataFrame(registros)
                st.dataframe(df_registros[["id_registro", "status", "prioridade", "observacao", "responsavel"]], hide_index=True, use_container_width=True)
            else:
                st.info("Este município ainda não possui registros.")

            st.divider()
            st.subheader("Adicionar registro")

            with st.form(f"criar_registro_{id_municipio}"):
                status = st.text_input("Status", key=f"novo_status_{id_municipio}")
                prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"], key=f"nova_prioridade_{id_municipio}")
                observacao = st.text_area("Observação", key=f"nova_observacao_{id_municipio}")
                responsavel = st.text_input("Responsável", key=f"novo_responsavel_{id_municipio}")
                criar = st.form_submit_button("Adicionar registro")

            if criar:
                if not status.strip():
                    st.warning("Informe o status.")
                else:
                    dados = {
                        "status": status,
                        "prioridade": prioridade,
                        "observacao": observacao,
                        "responsavel": responsavel
                    }
                    resposta = requests.post(f"{API_URL}/municipios/{id_municipio}/registros", json=dados, timeout=5)
                    mostrar_resultado(resposta, "Registro criado com sucesso!", "Não foi possível criar o registro.")

            if registros:
                st.divider()
                st.subheader("Editar ou remover registro")

                opcoes_registros = {
                    f"Registro {registro['id_registro']} - {registro['status']}": registro["id_registro"]
                    for registro in registros
                }
                registro_selecionado = st.selectbox("Selecione o registro", list(opcoes_registros.keys()), key="registro_selecionado")
                id_registro = opcoes_registros[registro_selecionado]
                registro = next(r for r in registros if r["id_registro"] == id_registro)

                with st.form(f"editar_registro_{id_registro}"):
                    novo_status = st.text_input("Status", value=registro["status"], key=f"status_registro_{id_registro}")
                    nova_prioridade = st.text_input("Prioridade", value=registro["prioridade"], key=f"prioridade_registro_{id_registro}")
                    nova_observacao = st.text_area("Observação", value=registro["observacao"] or "", key=f"observacao_registro_{id_registro}")
                    novo_responsavel = st.text_input("Responsável", value=registro["responsavel"] or "", key=f"responsavel_registro_{id_registro}")
                    atualizar = st.form_submit_button("Atualizar registro")

                if atualizar:
                    dados = {
                        "status": novo_status,
                        "prioridade": nova_prioridade,
                        "observacao": nova_observacao,
                        "responsavel": novo_responsavel
                    }
                    resposta = requests.put(f"{API_URL}/registros/{id_registro}", json=dados, timeout=5)
                    mostrar_resultado(resposta, "Registro atualizado com sucesso!", "Não foi possível atualizar o registro.")

                if st.button("Remover registro", key=f"remover_registro_{id_registro}"):
                    resposta = requests.delete(f"{API_URL}/registros/{id_registro}", timeout=5)
                    mostrar_resultado(resposta, "Registro removido com sucesso!", "Não foi possível remover o registro.")

        else:
            st.info("Nenhum município encontrado.")