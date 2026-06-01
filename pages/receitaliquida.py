import streamlit as st
import login
import locale
import time
import plotly.express as px
from pages.sql_conn import create_connection, fetch_receitaliquidaAtual_data

login.generarLogin()
if 'usuario' in st.session_state:
    # Configurar locale para o formato brasileiro
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    # Configurar o CSS
    with open('estilos.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    conn = create_connection()
    if conn:
        if 'ano' not in st.session_state:
                st.error("Por favor, selecione o ano antes de continuar.")
                time.sleep(3)       
                st.rerun()
        else:              
            ano_selecionado  = st.session_state['ano']
            df_display = fetch_receitaliquidaAtual_data(conn, ano_selecionado)
            st.subheader("Tabelas e Gráficos do Banco de Dados")
            df_display = df_display.rename(columns={
                'nm_itens_grupo_receita': 'Nome do Grupo',
                'total_vl_liquido': 'Faturamento Bruto Líquido',
                'total_vl_devolucoesvendas': 'Devolucoes Vendas',
                'total_vl_devolucoesservicos': 'Devolucoes Servicos',
                'receita_liquida': 'Receita Líquida'
            })
            # Formatar valores como moeda apenas para exibição na tabela
            df_tabela = df_display.copy()
            for col in ['Faturamento Bruto Líquido', 'Devolucoes Vendas', 'Devolucoes Servicos', 'Receita Líquida']:
                df_tabela[col] = df_tabela[col].apply(lambda x: locale.currency(x, grouping=True))
            if st.checkbox("Mostrar a Tabela da Receita Líquida Bruta"):
                st.subheader(f" 📋 Listagem da Receita Líquida Bruta - {ano_selecionado}")
                st.dataframe(df_tabela[['Nome do Grupo', 'Faturamento Bruto Líquido',
                            'Devolucoes Vendas', 'Devolucoes Servicos', 'Receita Líquida']])            
            # Filtro de Grupos (MultiSelect)
            st.sidebar.header("📦 Filtrar os Grupos")
            df = df_display.sort_values("Nome do Grupo")
            grupos = st.sidebar.multiselect(
                "Selecione o(s) Grupo(s):",
                options=df["Nome do Grupo"].unique(),
                default=df["Nome do Grupo"].unique())
            # Filtrar o(s) Grupo(s)
            if grupos:
                df = df[df["Nome do Grupo"].isin(grupos)]
            df = df.groupby("Nome do Grupo")["Receita Líquida"].sum().reset_index()
            df = df.sort_values(by="Receita Líquida", ascending=True)
            # Criar Grafico
            st.subheader(f"Gráfico de Receita Líquida em {ano_selecionado}")
            fig = px.bar(
                df, x= "Receita Líquida", y= "Nome do Grupo",
                title=" 📈 Total de Receita Líquida",
                labels={"Nome do Grupo": "Grupo",
                        "Receita Líquida": "Total da Receita Líquida"},
                color="Nome do Grupo",
                orientation="h")
            st.plotly_chart(fig)
        conn.close()
        print("Conexão encerrada com sucesso.")
    else:
        st.error("Não foi possivel conectar ao banco de dados.")
