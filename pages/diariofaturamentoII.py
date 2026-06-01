import streamlit as st
import login
import pandas as pd
import plotly.express as px
import locale
import time
from datetime import date
from pages.sql_conn import create_connection, fetch_diarioportugues_data

login.generarLogin()
if 'usuario' in st.session_state:
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
            ano_selecionado  = int(st.session_state['ano']) 
            df_display = fetch_diarioportugues_data(conn, ano_selecionado)
            df_display['Total de Faturamento'] = df_display['total_vl_total_nf'].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))   
            df = df_display       
            # Converter a coluna Data para datetime
            if df["dt_lancamento"].dtype in ["int64", "object"]:
                df["dt_lancamento"] = pd.to_datetime(df["dt_lancamento"], format="mixed", dayfirst=True)        
            # Remover o horário da coluna de data
            df["dt_lancamento"] = df["dt_lancamento"].dt.date
            # Ordenar por data
            df = df.sort_values("dt_lancamento")
            # Definir a coluna "data" como índice
            df = df.set_index("dt_lancamento")
            df_display = df_display.rename(columns={
                'dt_lancamento': 'Data',
                'nm_itens_grupo_receita': 'Grupo de Receita',
                'total_vl_total_nf': 'Total Faturamento'
            })        
            # Filtro de Grupos (MultiSelect)
            st.sidebar.header("📦 Filtrar Grupo de Receita")
            grupos = st.sidebar.multiselect(
                "Selecione um dos Grupo de Receita:",
                options=df_display["Grupo de Receita"].unique())
            if grupos:
                df_display = df_display[df_display["Grupo de Receita"].isin(grupos)]
                # Definir valores padrão para as datas
                data_min_default = date(ano_selecionado, 1, 1)  # Data Inicial padrão
                data_max_default = date(ano_selecionado, 12, 31)  # Data Final padrão
                # Filtro as Datas
                st.sidebar.header("📅 Filtrar por Datas")
                data_min = st.sidebar.date_input("Data Inicial", value=data_min_default, format='DD/MM/YYYY')
                data_max = st.sidebar.date_input("Data Final", value=data_max_default, format='DD/MM/YYYY')           
                if data_min > data_max:
                    #st.sidebar.error("A Data Inicial não pode ser maior que a Data Final.")
                    st.markdown(":blue-background[O Mês Inicial não pode ser maior que o Mês Final.]")
                else: 
                    #Aplicar filtro de dadas no Dataframe              
                    df_display["Data"] = pd.to_datetime(df_display["Data"], format='%d/%m/%Y')
                    filtered_df = df_display[(df_display["Data"].dt.date >= data_min) & (df_display["Data"].dt.date <= data_max)]
                    # Formatar a coluna 'Data' para o formato brasileiro 'DD/MM/YYYY'
                    filtered_df["Data"] = filtered_df["Data"].dt.strftime('%d/%m/%Y')                   
                    # Mostrar a tabela filtrada
                    st.subheader("Tabelas e Graficos do Banco de dados")               
                    if st.checkbox("Mostrar a Tabela Diário do Faturamento"):
                        st.subheader(f"📋 Listagem Diário de Faturamento - {ano_selecionado}")            
                        st.dataframe(filtered_df[['Data', 'Grupo de Receita', 'Total de Faturamento']])           
                    # Criar gráfico de linha com Plotly
                    st.subheader(f"Gráfico de Linhas - Faturamento Diário - {ano_selecionado}")
                    fig = px.line(filtered_df, x='Data', y='Total Faturamento',
                                markers=True,
                                color='Grupo de Receita',
                                title='Total de Faturamento por Data')
                    # Exibir gráfico no Streamlit
                    st.plotly_chart(fig)
                    # Criar gráfico de área empilhada
                    fig = px.area(
                        filtered_df,
                        x='Data',
                        y='Total Faturamento',
                        color='Grupo de Receita',  
                        title='Total de Faturamento por Data '
                    )
                    st.subheader("Faturamento Diário - Gráfico de Áreas Empilhadas")
                    st.plotly_chart(fig)
            else:
                st.toast('No canto inferior esquerdo da Tela') 
                st.toast('Por Favor selecionar o filtro e a data!!!') 
        conn.close()
        print("Conexão encerrada com sucesso.")
    else:
        st.error("Não foi possivel conectar ao banco de dados.")             
