import streamlit as st
import psycopg2
import pandas as pd

# Recupera os segredos do arquivo secrets.toml
host = st.secrets["connections"]["postgresql"]["host"]
port = st.secrets["connections"]["postgresql"].get("port", "6543")
database = st.secrets["connections"]["postgresql"]["database"]
username = st.secrets["connections"]["postgresql"]["username"]
password = st.secrets["connections"]["postgresql"]["password"]

# Conexão com o banco de dados (não cacheada) com definição de fuso horário
def get_db_connection():
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=username,
        password=password
    )
    # Define o fuso horário para America/Sao_Paulo (UTC-3)
    conn.cursor().execute("SET TIME ZONE 'America/Sao_Paulo';")
    return conn

# Função para buscar a lista de lojas (cacheada)
@st.cache_data
def get_lojas():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM lojas ORDER BY nome")
            lojas = cursor.fetchall()
    return lojas

# Função para buscar a lista de produtos (cacheada)
@st.cache_data
def get_produtos():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, nome, categoria, unidade_medida, valor  
                FROM produtos 
                ORDER BY nome
            """)
            produtos = cursor.fetchall()
    return produtos

# Função para buscar o estoque atual de uma loja
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

# Função para cadastrar um novo produto
def cadastrar_novo_produto(nome, categoria, unidade_medida, valor):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM produtos")
            max_id = cursor.fetchone()[0]
            new_id = max_id + 1 if max_id is not None else 1
            cursor.execute("""
                INSERT INTO produtos (id, nome, categoria, unidade_medida, valor)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_id, nome, categoria, unidade_medida, valor))
        conn.commit()
    return new_id

# Função para registrar entradas de estoque
def registrar_entrada(loja_id, itens):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for item in itens:
                produto_id = item['id']
                quantidade = item['quantidade']
                motivo = item['motivo'] if item['motivo'] else 'Entrada de estoque'
                cursor.execute("""
                    INSERT INTO movimentacoes_estoque (tipo, produto_id, loja_id, quantidade, motivo, data)
                    VALUES ('entrada', %s, %s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                """, (produto_id, loja_id, quantidade, motivo))
                cursor.execute("""
                    INSERT INTO estoque (loja_id, produto_id, quantidade, data_atualizacao)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    ON CONFLICT (loja_id, produto_id)
                    DO UPDATE SET quantidade = estoque.quantidade + %s, data_atualizacao = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'
                """, (loja_id, produto_id, quantidade, quantidade))
        conn.commit()

# Função para atualizar o estoque físico
def atualizar_estoque(loja_id, estoque_atual_input, data_contagem):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for produto_id, novo_valor in estoque_atual_input.items():
                cursor.execute("SELECT quantidade FROM estoque WHERE loja_id = %s AND produto_id = %s", (loja_id, produto_id))
                result = cursor.fetchone()
                current_qtd = result[0] if result else 0
                diferenca = current_qtd - novo_valor
                if diferenca > 0:
                    cursor.execute("""
                        INSERT INTO movimentacoes_estoque (tipo, produto_id, loja_id, quantidade, motivo, data)
                        VALUES ('saida', %s, %s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    """, (produto_id, loja_id, diferenca, 'Ajuste de estoque - saída'))
                elif diferenca < 0:
                    cursor.execute("""
                        INSERT INTO movimentacoes_estoque (tipo, produto_id, loja_id, quantidade, motivo, data)
                        VALUES ('entrada', %s, %s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
                    """, (produto_id, loja_id, abs(diferenca), 'Ajuste de estoque - entrada'))
                cursor.execute("""
                    INSERT INTO estoque (loja_id, produto_id, quantidade, data_atualizacao, data_contagem)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', %s)
                    ON CONFLICT (loja_id, produto_id)
                    DO UPDATE SET quantidade = %s, data_atualizacao = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', data_contagem = %s
                """, (loja_id, produto_id, novo_valor, data_contagem, novo_valor, data_contagem))
        conn.commit()

# Função para registrar alerta de validade (ATUALIZADA para incluir observacao como opcional)
def registrar_alerta_validade(loja_id, produto_id, quantidade, vencimento, observacao=None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO alerta_validade (produto_id, loja_id, data, vencimento, quantidade, observacao)
                VALUES (%s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', %s, %s, %s)
            """, (produto_id, loja_id, vencimento, quantidade, observacao))
        conn.commit()

# Função para selecionar loja (AJUSTADA para permitir troca de loja)
def select_store():
    if 'loja_confirmada' not in st.session_state:
        st.session_state.loja_confirmada = None
    
    if st.session_state.loja_confirmada is None:
        lojas = get_lojas()
        loja_options = {nome: id_loja for id_loja, nome in lojas}
        selected_loja = st.selectbox("Selecione a Loja", list(loja_options.keys()))
        if selected_loja:
            st.write(f"Você selecionou a loja **{selected_loja}**. Confirma a seleção?")
            if st.button("Confirmar Loja"):
                st.session_state.loja_confirmada = (loja_options[selected_loja], selected_loja)
                st.success(f"Loja **{selected_loja}** confirmada!")
                st.rerun()
        return None
    else:
        loja_id, loja_nome = st.session_state.loja_confirmada
        st.write(f"Loja selecionada: **{loja_nome}**")
        if st.button("Trocar Loja"):
            st.session_state.loja_confirmada = None
            st.rerun()
        return st.session_state.loja_confirmada


def registrar_saida_planilha(loja_id: int, itens: list[dict], data_saida):
    """
    Recebe:
    - loja_id: int
    - itens: lista de dicts com chaves 'produto_id' e 'quantidade'
    - data_saida: datetime.datetime ou date

    Para cada item, registra:
    1) uma movimentação de tipo 'saida' em movimentacoes_estoque
    2) decrementa o estoque na tabela estoque
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for item in itens:
                produto_id = int(item['produto_id'])
                quantidade  = int(item['quantidade'])

                # 1) Movimentação de saída
                cursor.execute("""
                    INSERT INTO movimentacoes_estoque
                      (tipo, produto_id, loja_id, quantidade, motivo, data)
                    VALUES
                      ('saida', %s, %s, %s, 'Saída diária', %s)
                """, (produto_id, loja_id, quantidade, data_saida))

                # 2) Atualização do estoque (subtraindo)
                cursor.execute("""
                    INSERT INTO estoque
                      (loja_id, produto_id, quantidade, data_atualizacao)
                    VALUES
                      (%s, %s, -%s, %s)
                    ON CONFLICT (loja_id, produto_id)
                    DO UPDATE
                      SET quantidade = estoque.quantidade - %s,
                          data_atualizacao = %s
                """, (loja_id, produto_id, quantidade, data_saida, quantidade, data_saida))

        conn.commit()        
