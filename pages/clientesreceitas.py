import streamlit as st
import login
import pandas as pd
import time
import plotly.express as px
from pages.sql_conn import create_connection, fetch_clientereceita_data

login.generarLogin()
if 'usuario' in st.session_state:   
    conn = create_connection()
    if conn:
        st.subheader("Tabelas e Gráficos do Banco de Dados")
        if 'ano' not in st.session_state:
                st.error("Por favor, selecione o ano antes de continuar.")
                time.sleep(3)       
                st.rerun()
        else:
            ano_selecionado  = st.session_state['ano']        
            df_display = fetch_clientereceita_data(conn, ano_selecionado )
            # Renomeiar as colunas
            df_display = df_display.rename(columns={
                'nm_itens_grupo_receita': 'Grupo de Receita',
                'nm_Cliente': 'Nome do Cliente',        
                'total_vl_total_nf': 'Total Faturamento'
            }) 
            df_display['Total de Faturamento'] = df_display['Total Faturamento'].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))           
            # Filtro de Grupos (MultiSelect)
            st.sidebar.header("📦 Filtrar os Grupos de Receita")     
            grupos = st.sidebar.multiselect(
                "Selecione o(s) Grupo(s):",
                options=df_display["Grupo de Receita"].unique()) 
            if grupos:
                df_display = df_display[df_display["Grupo de Receita"].isin(grupos)] 
        # Configurar as guias
            guia_tabela, guia_grafico,  guia_graficopie= st.tabs(["📊 Tabela", "📈 Gráfico de Barra", "🥧 Gráfico da Pizza" ])
            with guia_tabela:        
                st.subheader(f" 📋 Listagem de Clientes com Grupo da Receita - {ano_selecionado}")
                st.dataframe(df_display[['Grupo de Receita', 'Nome do Cliente', 'Total de Faturamento']])
            with guia_grafico:  
                st.subheader(f"📈  Gráfico de Barras - Cliente e Grupo - {ano_selecionado}")
                fig_bar = px.bar(
                    df_display,
                    x="Total Faturamento", y="Nome do Cliente",
                    title=" Total de Receita por Cliente e Grupo",
                    labels={"Nome do Cliente": "Cliente", "Total Faturamento": "Faturamento"},
                    color="Grupo de Receita",
                    height=400,   
                    orientation="h")
                # Mostrar Graficos
                st.plotly_chart(fig_bar, use_container_width=True)      
            with guia_graficopie:  
                # Gráfico de Pizza
                st.subheader(f"🥧 Gráfico de Pizza em {ano_selecionado}")
                df_display['Porcentagem'] = (df_display["Total Faturamento"] / df_display["Total Faturamento"].sum()) * 100
                threshold = 3  # Percentual mínimo para aparecer no gráfico
                outros = df_display[df_display['Porcentagem'] < threshold].sum(numeric_only=True)
                outros_label = pd.DataFrame({
                    'Nome do Cliente': ['Outros'],
                    'Total Faturamento': [outros['Total Faturamento']],
                    'Porcentagem': [outros['Porcentagem']]
                })
                df_maiores = df_display[df_display['Porcentagem'] >= threshold]
                df_final = pd.concat([df_maiores, outros_label], ignore_index=True)
                # Criar gráfico de pizza com Plotly
                fig_pizza = px.pie(
                    df_final,
                    names='Nome do Cliente',
                    values='Total Faturamento',
                    title=" Grupos de Receita em Porcentagem",
                    hole=0.3,
                )
                st.plotly_chart(fig_pizza)        
        conn.close()
        print("Conexão encerrada com sucesso.")
    else:
        st.error("Não foi possivel conectar ao banco de dados.")
