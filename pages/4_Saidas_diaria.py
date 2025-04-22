# --- Novo arquivo: estoque_mome/pages/4_Saida_Diaria.py ---

import streamlit as st
import pandas as pd
import datetime as dt
from utils import get_lojas, registrar_saida_planilha

st.set_page_config(page_title="Saída Diária", layout="wide")

def page_saida_diaria():
    st.title("Saída Diária de Estoque")

    # 1) Seleção da loja
    lojas = get_lojas()
    if not lojas:
        st.error("Nenhuma loja cadastrada. Cadastre antes de continuar.")
        return
    lojas_dict = {f"{id_} – {nome}": id_ for id_, nome in lojas}
    loja_sel = st.selectbox("Selecione a loja", list(lojas_dict.keys()))
    loja_id = lojas_dict[loja_sel]

    # 2) Upload da planilha
    st.markdown("Faça upload de uma planilha CSV ou Excel com colunas: `cod`, `produto`, `quantidade`.")
    uploaded = st.file_uploader("Arquivo de Saída", type=["csv", "xlsx"])
    if uploaded:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)

        # Armazena para edição
        st.session_state['df_saida'] = df

    # 3) Edição e data
    if 'df_saida' in st.session_state:
        df_edit = st.data_editor(
            st.session_state['df_saida'],
            num_rows="dynamic",
            column_config={
                "cod":     st.column_config.NumberColumn("cod", required=True),
                "produto": st.column_config.TextColumn("produto", disabled=True),
                "quantidade": st.column_config.NumberColumn("quantidade", required=True, min_value=1)
            }
        )
        st.session_state['df_saida'] = df_edit

        data_saida = st.date_input("Data da Saída", value=dt.date.today())

        if st.button("Registrar Saídas"):
            # Prepara itens e chama a função de utils
            itens = [
                {"produto_id": row["cod"], "quantidade": row["quantidade"]}
                for _, row in df_edit.iterrows()
            ]
            timestamp = dt.datetime.combine(data_saida, dt.datetime.now().time())
            registrar_saida_planilha(loja_id, itens, timestamp)

            st.success("Saídas registradas com sucesso!")
            del st.session_state['df_saida']

def main():
    page_saida_diaria()

if __name__ == "__main__":
    main()
