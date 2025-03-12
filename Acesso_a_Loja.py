import streamlit as st
from utils import select_store

st.set_page_config(page_title="Acesso à Loja", layout="wide")

def main():
    st.title("Acesso à Loja")
    select_store()

if __name__ == "__main__":
    main()