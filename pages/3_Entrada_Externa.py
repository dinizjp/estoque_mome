import streamlit as st
from utils import select_store, get_produtos, registrar_entrada

st.set_page_config(page_title="Entrada de Estoque", layout="wide")

def main():
    st.title("Entrada de Estoque")
    
    loja_info = select_store()
    if loja_info is None:
        st.warning("Por favor, selecione uma loja.")
        return
    
    loja_id, loja_nome = loja_info
    st.write(f"Registrando entrada para a loja: **{loja_nome}**")
    
    produtos = get_produtos()
    produto_selecionado = st.selectbox("Selecione o produto", produtos,
                                       format_func=lambda p: f"{p[0]} - {p[1]}")
    
    quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)
    motivo = st.text_input("Motivo da entrada (opcional)")
    
    if 'itens_entrada' not in st.session_state:
        st.session_state.itens_entrada = []
    
    if produto_selecionado and st.button("Adicionar Produto à Lista"):
        st.session_state.itens_entrada.append({
            'id': produto_selecionado[0],
            'nome': produto_selecionado[1],
            'quantidade': quantidade,
            'motivo': motivo
        })
        st.success(f"Produto **{produto_selecionado[1]}** adicionado à lista!")
        
    if st.session_state.itens_entrada:
        st.markdown("### Itens para Entrada")
        for i, item in enumerate(st.session_state.itens_entrada):
            col1, col2, col3, col4 = st.columns([3, 1, 3, 1])
            with col1:
                st.write(f"{item['nome']} (ID: {item['id']})")
            with col2:
                novo_qtd = st.number_input("Qtd", min_value=1, step=1, value=item['quantidade'], key=f"entrada_qtd_{i}")
                item['quantidade'] = novo_qtd
            with col3:
                st.write(item['motivo'] if item['motivo'] else "Sem motivo")
            with col4:
                if st.button("Remover", key=f"remove_{i}"):
                    st.session_state.itens_entrada.pop(i)
                    
    
    if st.button("Confirmar Entrada"):
        if not st.session_state.itens_entrada:
            st.error("Adicione pelo menos um item antes de confirmar.")
        else:
            registrar_entrada(loja_id, st.session_state.itens_entrada)
            st.success("Entrada registrada com sucesso!")
            st.session_state.itens_entrada = []
            

if __name__ == "__main__":
    main()