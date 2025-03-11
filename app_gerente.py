import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(
    page_title='Programa Estoque',
    layout='wide'
)

# # Recupera os segredos do arquivo secrets.toml
# host = st.secrets["connections"]["postgresql"]["host"]
# port = st.secrets["connections"]["postgresql"].get("port", "5432")
# database = st.secrets["connections"]["postgresql"]["database"]
# username = st.secrets["connections"]["postgresql"]["username"]
# password = st.secrets["connections"]["postgresql"]["password"]

# Conexão com o banco de dados (não cacheada)
def get_db_connection():
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=username,
        password=password
    )
    return conn

# Função para buscar a lista de lojas
@st.cache_data
def get_lojas():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM lojas ORDER BY nome")
            lojas = cursor.fetchall()
    return lojas

# Função para buscar a lista de produtos (com informações adicionais)
@st.cache_data
def get_produtos():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, nome, categoria, unidade_medida, valor,  
                FROM produtos 
                ORDER BY nome
            """)
            produtos = cursor.fetchall()
    return produtos

# Função para buscar o estoque atual de uma loja (join com produtos para exibir nome)
def get_estoque_loja(loja_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            query = """
                SELECT e.produto_id, p.nome, e.quantidade
                FROM estoque e
                JOIN produtos p ON e.produto_id = p.id
                WHERE e.loja_id = %s
            """
            cursor.execute(query, (loja_id,))
            estoque = cursor.fetchall()
    return estoque

# Função para cadastrar um novo produto (para produtos não cadastrados)
def cadastrar_novo_produto(nome, categoria, unidade_medida, valor ):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM produtos")
            max_id = cursor.fetchone()[0]
            new_id = max_id + 1 if max_id is not None else 1
            cursor.execute("""
                INSERT INTO produtos (id, nome, categoria, unidade_medida, valor )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_id, nome, categoria, unidade_medida, valor))
        conn.commit()
    return new_id

# Função para registrar entradas de estoque e atualizar a tabela estoque
def registrar_entrada(loja_id, itens):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for item in itens:
                produto_id = item['id']
                quantidade = item['quantidade']
                motivo = item['motivo'] if item['motivo'] else 'Entrada de estoque'
                # Registrar movimentação do tipo 'entrada' usando a coluna "data"
                cursor.execute("""
                    INSERT INTO movimentacoes_estoque (tipo, produto_id, loja_id, quantidade, motivo, data)
                    VALUES ('entrada', %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (produto_id, loja_id, quantidade, motivo))
                # Atualizar ou inserir no estoque (soma a quantidade já existente)
                cursor.execute("""
                    INSERT INTO estoque (loja_id, produto_id, quantidade, data_atualizacao)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (loja_id, produto_id)
                    DO UPDATE SET quantidade = estoque.quantidade + %s, data_atualizacao = CURRENT_TIMESTAMP
                """, (loja_id, produto_id, quantidade, quantidade))
        conn.commit()

# Função para atualizar o estoque físico e registrar as diferenças em movimentações
def atualizar_estoque(loja_id, estoque_atual_input):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for produto_id, novo_valor in estoque_atual_input.items():
                # Busca o estoque atual registrado no banco
                cursor.execute("SELECT quantidade FROM estoque WHERE loja_id = %s AND produto_id = %s", (loja_id, produto_id))
                result = cursor.fetchone()
                current_qtd = result[0] if result else 0
                diferenca = current_qtd - novo_valor
                if diferenca > 0:
                    # Se o estoque físico é menor, registra saída usando a coluna "data"
                    cursor.execute("""
                        INSERT INTO movimentacoes_estoque (tipo, produto_id, loja_id, quantidade, motivo, data)
                        VALUES ('saida', %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """, (produto_id, loja_id, diferenca, 'Ajuste de estoque - saída'))
                elif diferenca < 0:
                    # Se o estoque físico é maior, registra entrada (ajuste) usando a coluna "data"
                    cursor.execute("""
                        INSERT INTO movimentacoes_estoque (tipo, produto_id, loja_id, quantidade, motivo, data)
                        VALUES ('entrada', %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """, (produto_id, loja_id, abs(diferenca), 'Ajuste de estoque - entrada'))
                # Atualiza o estoque com o valor físico informado
                cursor.execute("""
                    INSERT INTO estoque (loja_id, produto_id, quantidade, data_atualizacao)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (loja_id, produto_id)
                    DO UPDATE SET quantidade = %s, data_atualizacao = CURRENT_TIMESTAMP
                """, (loja_id, produto_id, novo_valor, novo_valor))
        conn.commit()

# Nova função para registrar alerta de validade
def registrar_alerta_validade(loja_id, produto_id, quantidade, vencimento):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO alerta_validade (produto_id, loja_id, data, vencimento, quantidade)
                VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)
            """, (produto_id, loja_id, vencimento, quantidade))
        conn.commit()

#####################################
# Página 1: Acesso à Loja
#####################################
def page_acesso_loja():
    st.title("Acesso à Loja")
    lojas = get_lojas()
    loja_options = {nome: id_loja for id_loja, nome in lojas}
    
    if 'loja_confirmada' not in st.session_state:
        st.session_state.loja_confirmada = None
    
    if st.session_state.loja_confirmada is None:
        selected_loja = st.selectbox("Selecione a Loja", list(loja_options.keys()))
        if selected_loja:
            st.write(f"Você selecionou a loja **{selected_loja}**. Confirma a seleção?")
            if st.button("Confirmar Loja"):
                st.session_state.loja_confirmada = (loja_options[selected_loja], selected_loja)
                st.success(f"Loja **{selected_loja}** confirmada!")
    else:
        loja_id, loja_nome = st.session_state.loja_confirmada
        st.write(f"Loja selecionada: **{loja_nome}**")
        if st.button("Trocar Loja"):
            st.session_state.loja_confirmada = None
            st.rerun()

#####################################
# Página 2: Entrada de Estoque
#####################################
def page_entrada_estoque():
    st.title("Entrada de Estoque")
    
    # Verifica se a loja foi confirmada
    if 'loja_confirmada' not in st.session_state or st.session_state.loja_confirmada is None:
        st.warning("Por favor, confirme a loja na página 'Acesso à Loja'.")
        return
    loja_id, loja_nome = st.session_state.loja_confirmada
    st.write(f"Registrando entrada para a loja: **{loja_nome}**")
    
    # Apresenta somente um selectbox para selecionar o produto
    produtos = get_produtos()
    produto_selecionado = st.selectbox("Selecione o produto", produtos,
                                       format_func=lambda p: f"{p[0]} - {p[1]}")
    
    quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)
    motivo = st.text_input("Motivo da entrada (opcional)")
    
    # Cache para armazenar os itens a serem registrados
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
    
    # Exibe e permite a edição dos itens a serem adicionados
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
                    st.rerun()
    
    if st.button("Confirmar Entrada"):
        if not st.session_state.itens_entrada:
            st.error("Adicione pelo menos um item antes de confirmar.")
        else:
            registrar_entrada(loja_id, st.session_state.itens_entrada)
            st.success("Entrada registrada com sucesso!")
            st.session_state.itens_entrada = []
            st.rerun()

#####################################
# Página 3: Estoque Atual e Ajustes
#####################################
def page_estoque_atual():
    st.title("Estoque Atual e Ajustes")
    
    # Verifica se a loja foi confirmada
    if 'loja_confirmada' not in st.session_state or st.session_state.loja_confirmada is None:
        st.warning("Por favor, confirme a loja na página 'Acesso à Loja'.")
        return
    loja_id, loja_nome = st.session_state.loja_confirmada
    st.write(f"Ajuste de estoque para a loja: **{loja_nome}**")
    
    # Inicializa a lista de atualizações se ainda não existir
    if 'estoque_updates' not in st.session_state:
        st.session_state.estoque_updates = []
    
    # Busca a lista de produtos e o estoque atual da loja
    produtos = get_produtos()
    estoque_atual = get_estoque_loja(loja_id)
    
    # Cria um dicionário com o estoque (produto_id: {nome, quantidade})
    estoque_dict = {p_id: {'nome': nome, 'quantidade': qtd} for p_id, nome, qtd in estoque_atual}
    # Para produtos sem registro, define quantidade como 0
    for p in produtos:
        pid = p[0]
        if pid not in estoque_dict:
            estoque_dict[pid] = {'nome': p[1], 'quantidade': 0}
    
    st.markdown("### Selecionar Produto para Atualizar Estoque")
    
    # Utiliza o mesmo padrão do selectbox da página de entrada de estoque
    selected_produto = st.selectbox("Selecione o produto", produtos, format_func=lambda p: f"{p[0]} - {p[1]}")
    selected_produto_id = selected_produto[0]
    
    # Exibe a quantidade atual para o produto selecionado
    current_qtd = estoque_dict[selected_produto_id]['quantidade']
    st.write(f"Quantidade atual: {current_qtd}")
    
    # Input para o novo valor do estoque para o produto selecionado
    novo_valor = st.number_input("Nova Quantidade", min_value=0, step=1, value=current_qtd, key=f"novo_qtd_{selected_produto_id}")
    
    # Botão para adicionar a atualização do produto à lista
    if st.button("Adicionar Atualização"):
        # Verifica se o produto já está na lista de atualizações e atualiza se necessário
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
        st.rerun()
    
    # Exibe a lista de atualizações selecionadas
    if st.session_state.estoque_updates:
        st.markdown("### Atualizações Selecionadas")
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
                    st.rerun()
    
    # Botão para confirmar todas as atualizações
    if st.button("Confirmar Ajustes"):
        updates_dict = {item['produto_id']: item['novo_valor'] for item in st.session_state.estoque_updates}
        atualizar_estoque(loja_id, updates_dict)
        st.success("Estoque atualizado e movimentações registradas com sucesso!")
        st.session_state.estoque_updates = []
        st.rerun()

#####################################
# Página 4: Alerta de Validade
#####################################
def page_alerta_validade():
    st.title("Alerta de Validade")
    
    # Verifica se a loja foi confirmada
    if 'loja_confirmada' not in st.session_state or st.session_state.loja_confirmada is None:
        st.warning("Por favor, confirme a loja na página 'Acesso à Loja'.")
        return
    loja_id, loja_nome = st.session_state.loja_confirmada
    st.write(f"Registrando alerta de validade para a loja: **{loja_nome}**")
    
    # Seleção do produto
    produtos = get_produtos()
    produto_selecionado = st.selectbox("Selecione o produto", produtos,
                                       format_func=lambda p: f"{p[0]} - {p[1]}")
    
    # Inputs para quantidade e vencimento (texto)
    quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)
    vencimento = st.text_input("Validade (observação)")
    
    # Cria um flag no session_state para evitar múltiplos registros
    if "alert_registrado" not in st.session_state:
        st.session_state.alert_registrado = False
    
    if st.button("Registrar Alerta", disabled=st.session_state.alert_registrado):
        if not vencimento:
            st.error("Informe a validade (observação).")
        else:
            registrar_alerta_validade(loja_id, produto_selecionado[0], quantidade, vencimento)
            st.success("Alerta de validade registrado com sucesso!")
            st.session_state.alert_registrado = True
            # Não chamamos st.rerun() para que a mensagem permaneça visível

#####################################
# Função principal com navegação
#####################################
def main():
    st.sidebar.title("Controle de Estoque")
    pagina = st.sidebar.radio("Navegação", ["Acesso à Loja", "Entrada de Estoque", "Estoque Atual", "Alerta de Validade"])
    
    if pagina == "Acesso à Loja":
        page_acesso_loja()
    elif pagina == "Entrada de Estoque":
        page_entrada_estoque()
    elif pagina == "Estoque Atual":
        page_estoque_atual()
    elif pagina == "Alerta de Validade":
        page_alerta_validade()

if __name__ == "__main__":
    main()