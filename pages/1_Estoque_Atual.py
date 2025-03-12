import streamlit as st
from utils import select_store, get_produtos, get_estoque_loja, atualizar_estoque
import time

st.set_page_config(page_title="Estoque Atual", layout="wide")

def main():
    st.title("Estoque Atual")
    
    loja_info = select_store()
    if loja_info is None:
        st.warning("Por favor, selecione uma loja.")
        return
    
    loja_id, loja_nome = loja_info
    st.write(f"Ajuste de estoque para a loja: **{loja_nome}**")
    
    if 'estoque_updates' not in st.session_state:
        st.session_state.estoque_updates = []
    
    produtos = get_produtos()
    estoque_atual = get_estoque_loja(loja_id)
    
    estoque_dict = {p_id: {'nome': nome, 'quantidade': qtd} for p_id, nome, qtd in estoque_atual}
    for p in produtos:
        pid = p[0]
        if pid not in estoque_dict:
            estoque_dict[pid] = {'nome': p[1], 'quantidade': 0}
    
    st.markdown("### Selecionar produto para atualizar estoque")
    
    selected_produto = st.selectbox("Selecione o produto", produtos, format_func=lambda p: f"{p[0]} - {p[1]}")
    selected_produto_id = selected_produto[0]
    
    current_qtd = estoque_dict[selected_produto_id]['quantidade']
    st.info(f"Quantidade em estoque: {current_qtd}")
    
    novo_valor = st.number_input("Quantidade atual", min_value=0, step=1, value=current_qtd, key=f"novo_qtd_{selected_produto_id}")
    
    if st.button("Adicionar atualização"):
        found = False
        for item in st.session_state.estoque_updates:
            if item['produto_id'] == selected_produto_id:
                item['novo_valor'] = novo_valor
                found = True
                break
        if not found:
            st.session_state.estoque_updates.append({
                'produto_id': selected_produto_id,
                'nome': estoque_dict[selected_produto_id]['nome'],
                'novo_valor': novo_valor
            })
        st.success(f"Atualização para {estoque_dict[selected_produto_id]['nome']} adicionada!")
       
        
       
    
    if st.session_state.estoque_updates:
        st.markdown("### Atualizações selecionadas")
        for i, item in enumerate(st.session_state.estoque_updates):
            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.write(f"{item['produto_id']} - {item['nome']}")
            with col2:
                new_val = st.number_input("Novo valor", min_value=0, step=1, value=item['novo_valor'], key=f"update_{item['produto_id']}")
                item['novo_valor'] = new_val
            with col3:
                if st.button("Remover", key=f"remove_{item['produto_id']}"):
                    st.session_state.estoque_updates.pop(i)
                   
    
    if st.button("Confirmar ajustes"):
        updates_dict = {item['produto_id']: item['novo_valor'] for item in st.session_state.estoque_updates}
        atualizar_estoque(loja_id, updates_dict)
        st.success("Estoque atualizado e movimentações registradas com sucesso!")
        st.session_state.estoque_updates = []
       

if __name__ == "__main__":
    main()