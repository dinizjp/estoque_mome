import streamlit as st
import pandas as pd
import datetime as dt
from utils import select_store, get_db_connection

st.set_page_config(page_title="Histórico Mensal", layout="wide")

def page_historico_movimentacoes():
    st.title("Histórico Mensal de Movimentações por Produto")

    # 1) Seleção da loja
    loja_info = select_store()
    if loja_info is None:
        st.warning("Por favor, selecione uma loja.")
        return
    loja_id, loja_nome = loja_info

    # 2) Filtro de período
    ano = st.number_input("Ano", min_value=2000, max_value=2100, value=dt.date.today().year)
    mes = st.selectbox("Mês", list(range(1,13)), index=dt.date.today().month-1)
    primeiro_dia = dt.date(ano, mes, 1)
    ultimo_dia   = (primeiro_dia + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)

    # 3) Consulta por produto
    sql = """
    WITH mov AS (
      SELECT produto_id,
             SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE 0 END) AS total_entradas,
             SUM(CASE WHEN tipo='saida'   THEN quantidade ELSE 0 END) AS total_saidas
      FROM movimentacoes_estoque
      WHERE loja_id = %s AND data BETWEEN %s AND %s
      GROUP BY produto_id
    ), stock AS (
      SELECT produto_id,
             quantidade      AS estoque_atual,
             data_contagem   AS ultima_contagem
      FROM estoque
      WHERE loja_id = %s
    )
    SELECT
      p.id         AS produto_id,
      p.nome       AS produto,
      COALESCE(m.total_entradas,0) AS total_entradas,
      COALESCE(m.total_saidas,0)   AS total_saidas,
      COALESCE(s.estoque_atual,0)   AS estoque_atual,
      s.ultima_contagem,
      (COALESCE(s.estoque_atual,0)
       + COALESCE(m.total_saidas,0)
       - COALESCE(m.total_entradas,0)
      ) AS estoque_inicial
    FROM produtos p
    LEFT JOIN mov AS m ON p.id = m.produto_id
    LEFT JOIN stock AS s ON p.id = s.produto_id
    ORDER BY p.nome
    """

    with get_db_connection() as conn:
        df = pd.read_sql(sql, conn, params=(loja_id, primeiro_dia, ultimo_dia, loja_id))

    # 4) Exibição
    st.subheader(f"{loja_nome} — {primeiro_dia.strftime('%B/%Y')}")
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    page_historico_movimentacoes()
