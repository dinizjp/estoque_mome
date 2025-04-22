#Saidas Diárias

import streamlit as st
import pandas as pd
import datetime as dt
from utils import select_store, registrar_saida_planilha

st.set_page_config(page_title="Saída Diária", layout="wide")

def page_saida_diaria():
    st.title("Saída Diária de Estoque")

    # 1) Seleção e confirmação da loja
    loja_info = select_store()
    if loja_info is None:
        st.warning("Por favor, selecione uma loja.")
        return
    loja_id, loja_nome = loja_info

    # 2) Upload da planilha
    st.markdown("Faça upload de uma planilha CSV ou Excel com colunas: `cod`, `produto`, `quantidade`.")
    uploaded = st.file_uploader("Arquivo de Saída", type=["csv", "xlsx"])
    if uploaded:
        # lê o arquivo
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
        # remove linhas com quantidade zero
        df = df[df["quantidade"] != 0].reset_index(drop=True)
        # armazena para edição
        st.session_state['df_saida'] = df

    # 3) Edição e data
    if 'df_saida' in st.session_state and not st.session_state['df_saida'].empty:
        df_edit = st.data_editor(
            st.session_state['df_saida'],
            num_rows="dynamic",
            column_config={
                "cod": st.column_config.NumberColumn("cod", required=True),
                "produto": st.column_config.TextColumn("produto", disabled=True),
                "quantidade": st.column_config.NumberColumn("quantidade", required=True, min_value=1)
            }
        )
        st.session_state['df_saida'] = df_edit

        data_saida = st.date_input("Data da Saída", value=dt.date.today())

        if st.button("Registrar Saídas"):
            # garante que zero não entra
            df_final = st.session_state['df_saida']
            df_final = df_final[df_final["quantidade"] != 0]
            if df_final.empty:
                st.warning("Nenhum item com quantidade > 0 para registrar.")
            else:
                itens = [
                    {"produto_id": int(row["cod"]), "quantidade": int(row["quantidade"])}
                    for _, row in df_final.iterrows()
                ]
                timestamp = dt.datetime.combine(data_saida, dt.datetime.now().time())
                registrar_saida_planilha(loja_id, itens, timestamp)

                st.success("Saídas registradas com sucesso!")
            # limpa para novo uso
            del st.session_state['df_saida']

def main():
    page_saida_diaria()

if __name__ == "__main__":
    main()
