# Em pages/Alerta_de_Validade.py

import streamlit as st
from utils import select_store, get_produtos, registrar_alerta_validade
from datetime import date

st.set_page_config(page_title="Alerta de Validade", layout="wide")

def main():
    st.title("Alerta de Validade")
    
    # Seleção da loja (lógica existente mantida)
    loja_info = select_store()
    if loja_info is None:
        st.warning("Por favor, selecione uma loja.")
        return
    
    loja_id, loja_nome = loja_info
    st.write(f"Registrando alerta de validade para a loja: **{loja_nome}**")
    
    # Selectbox para o produto (vinculado a produto_id), exibindo ID e nome
    produtos = get_produtos()
    produto_selecionado = st.selectbox(
        "Selecione o Produto",
        produtos,
        format_func=lambda p: f"{p[0]} - {p[1]}"  # Exibe "ID - Nome"
    )
    
    # Input numérico para a quantidade (vinculado a quantidade)
    quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)
    
    # Input de data para a data de vencimento (vinculado a vencimento)
    vencimento = st.date_input("Data de Vencimento", value=None, min_value=date.today())
    
    # Input de texto para observações (vinculado a observacao)
    observacao = st.text_area("Observações (opcional)", height=100)
    
    # Botão para registrar o alerta
    if st.button("Registrar Alerta"):
        if not produto_selecionado:
            st.error("Selecione um produto.")
        elif not vencimento:
            st.error("Informe a data de vencimento.")
        else:
            registrar_alerta_validade(
                loja_id=loja_id,
                produto_id=produto_selecionado[0],  # Pega o ID do produto
                quantidade=quantidade,
                vencimento=vencimento,
                observacao=observacao
            )
            st.success("Alerta de validade registrado com sucesso!")
            
            
if __name__ == "__main__":
    main()