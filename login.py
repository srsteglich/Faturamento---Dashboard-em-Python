import streamlit as st
import hashlib
import pandas as pd
from sql_local import fetch_data
from pages.sql_conn import create_connection, fetch_ano

# Validação simples de usuário e senha com um arquivo csv
def validarUsuario(usuario, senha):
    senha_hash = hashlib.md5(senha.encode()).hexdigest()
    query = """SELECT u.id_usuario, u.nm_usuario
                FROM ADV_Usuarios u
                JOIN ADV_Sehnas s ON u.id_usuario = s.id_usuario
                WHERE u.nm_usuario = %s AND s.nm_senha = %s AND u.bo_ativo = true AND s.bo_ativo = true"""
    conn = fetch_data()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (usuario, senha_hash))
            result = cur.fetchone()
            if result:
                return True
            return False
    finally:
        conn.close()

# Função para armazenar o ano selecionado na sessão
def store_value():
    if '_ano' in st.session_state:
        st.session_state['ano'] = st.session_state['_ano']

def generarMenu(usuario):
    with st.sidebar:
        conn = fetch_data()
        try:
            with conn.cursor() as cur:
                cur.execute("""SELECT nm_usuario FROM ADV_Usuarios
                                WHERE nm_usuario = %s AND bo_ativo = TRUE""", (usuario,))
                result = cur.fetchone()
                if result:
                    nome = result[0]
                    st.subheader(f" **:gray-background[ Olá, {nome} ]** ")
                else:
                    st.error("Usuário não encontrado ou inativo.")
        finally:
            conn.close()

        st.page_link("app.py", label="🏠 Início")
        conn = create_connection()
        df_anos = fetch_ano(conn)
        anos_disponiveis = df_anos['ano'].astype(str).tolist()

        # Define o último ano disponível por padrão, caso ainda não esteja na sessão
        if 'ano' not in st.session_state:
            st.session_state['ano'] = anos_disponiveis[-1]
       
        ano_selecionado = st.selectbox(
            "Selecione o Ano", 
            anos_disponiveis, 
            index=anos_disponiveis.index(st.session_state['ano']),
            key="_ano", 
            on_change=store_value
        )

        st.header("👨‍💻👩‍💻 :blue[Clientes]")
        st.page_link("pages/clientes.py", label="Painel Top 10 Clientes")
        st.page_link("pages/clientesreceitas.py",
                     label="Painel dos Clientes e Grupos de Receitas")
        st.header(" $  󠀤 :blue[Faturamentos]")
        st.page_link("pages/faturamento.py",
                     label="Painel dos Faturamentos Brutos")
        st.page_link("pages/mensalfaturamento.py",
                     label="Painel Mensal dos Faturamentos Brutos")
        st.page_link("pages/receitaliquida.py",
                     label="Painel Receita Bruta Líquida de Vendas")
        st.page_link("pages/diariofaturamento.py",
                     label="Painel Diário dos Faturamentos Brutos")
        st.page_link("pages/diariofaturamentoII.py",
                     label="Painel Diário dos Faturamentos Brutos II")

def generarLogin():
    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'])
    else:
        with st.form('frmLogin'):
            parUsuario = st.text_input('Usuario')
            parPassword = st.text_input('Password', type='password')
            btnLogin = st.form_submit_button('Entrar', type='primary')
            if btnLogin:
                if validarUsuario(parUsuario, parPassword):
                    st.session_state['usuario'] = parUsuario
                    st.rerun()
                else:
                    st.error("Nome de usuário ou senha inválidos",
                             icon=":material/gpp_maybe:")
                    
if __name__ == '__main__':
    generarLogin()                   
