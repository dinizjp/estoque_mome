import streamlit as st
import pandas as pd
import datetime as dt
from utils import select_store, registrar_alerta_validade

st.set_page_config(page_title="Alerta de Validade", layout="wide")

# Path to the Excel template; atualize caso mova o arquivo
TEMPLATE_PATH = "validade.xlsx"

def page_alerta_validade():
    st.title("Alerta de Validade em Lote")
    
    # 1) Seleção e confirmação de loja
    loja_info = select_store()
    if loja_info is None:
        st.warning("Por favor, selecione uma loja.")
        return
    loja_id, loja_nome = loja_info

    # 2) Download do template
    st.markdown(
        "Faça download do modelo de planilha e preencha as colunas: "
        "`produto_id`, `lote`, `data_vencimento` (YYYY-MM-DD), `quantidade`."
    )
    try:
        with open(TEMPLATE_PATH, "rb") as f:
            template_bytes = f.read()
        st.download_button(
            label="📥 Baixar Modelo de Planilha de Validade",
            data=template_bytes,
            file_name="validade_modelo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except FileNotFoundError:
        st.error(f"Template não encontrado em {TEMPLATE_PATH}")

    # 3) Upload da planilha preenchida
    uploaded = st.file_uploader(
        "Selecione a planilha de validade",
        type=["xlsx", "xls", "csv"]
    )
    if uploaded:
        df = (
            pd.read_excel(uploaded)
            if uploaded.name.endswith((".xls", ".xlsx"))
            else pd.read_csv(uploaded)
        )
        expected = {"produto_id", "lote", "data_vencimento", "quantidade"}
        faltantes = expected - set(df.columns)
        if faltantes:
            st.error(f"Colunas obrigatórias não encontradas: {faltantes}")
            return

        # descarta zeros e reseta índice
        df = df[df["quantidade"] != 0].reset_index(drop=True)
        st.session_state["df_validade"] = df

    # 4) Edição interativa
    if "df_validade" in st.session_state and not st.session_state["df_validade"].empty:
        df_edit = st.data_editor(
            st.session_state["df_validade"],
            num_rows="dynamic",
            column_config={
                "produto_id":      st.column_config.NumberColumn("produto_id", required=True),
                "lote":            st.column_config.TextColumn("lote", required=True),
                "data_vencimento": st.column_config.DateColumn("data_vencimento", required=True),
                "quantidade":      st.column_config.NumberColumn("quantidade", required=True, min_value=1),
            }
        )
        st.session_state["df_validade"] = df_edit

        # 5) Registro automático com timestamp atual
        if st.button("Registrar Alertas em Lote"):
            timestamp = dt.datetime.now()
            for _, row in st.session_state["df_validade"].iterrows():
                registrar_alerta_validade(
                    loja_id=loja_id,
                    produto_id=int(row["produto_id"]),
                    quantidade=int(row["quantidade"]),
                    data_vencimento=row["data_vencimento"],
                    lote=row["lote"],
                    data=timestamp
                )
            st.success("Alertas de validade registrados com sucesso!")
            del st.session_state["df_validade"]

if __name__ == "__main__":
    page_alerta_validade()