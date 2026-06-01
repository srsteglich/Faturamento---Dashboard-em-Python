import streamlit as st
import login
import pandas as pd
import plotly.express as px
import locale
import time
from datetime import timedelta
from pages.sql_conn import create_connection, fetch_diariofaturamento_data

login.generarLogin()
if 'usuario' in st.session_state:
    conn = create_connection()
    if conn:   
        if 'ano' not in st.session_state:
                st.error("Por favor, selecione o ano antes de continuar.")
                time.sleep(3)       
                st.rerun()
        else:
            ano_selecionado  = int(st.session_state['ano']) 
            df_display = fetch_diariofaturamento_data(conn, ano_selecionado)
            df_display['Total de Faturamento'] = df_display['total_vl_total_nf'].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))   
            df = df_display        
            # Converter a coluna Data para datetime
            if df["dt_lancamento"].dtype in ["int64", "object"]:
                df["dt_lancamento"] = pd.to_datetime(
                    df["dt_lancamento"], infer_datetime_format=True)          
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
                # Filtro as Datas
                st.sidebar.header("📅 Filtrar por Datas")
                data_min = df.index.min()   
                data_max = df.index.max()
                intervalo = st.sidebar.slider(" Selecione o periodo da data",
                                            value=(data_min, data_max),
                                            min_value=data_min,
                                            max_value=data_max,                                 
                                            step=timedelta(days=30), # opção de 1 a 1, 15 a 15, 30 a 30 dias
                                            format="DD/MM/YYYY") 
                # Converter o intervalo para datetime.date
                intervalo = (intervalo[0], intervalo[1])
                # Aplicar o filtro de datas
                df_display["Data"] = pd.to_datetime(df_display["Data"])  # Garantir que a coluna Data seja datetime
                df_display = df_display[(df_display["Data"].dt.date >= intervalo[0]) & (df_display["Data"].dt.date <= intervalo[1])]
                # Mostrar a tabela filtrada
                st.subheader("Tabelas e Graficos do Banco de dados")               
                if st.checkbox("Mostrar a Tabela Diário do Faturamento"):
                    st.subheader(f"📋 Listagem Diário de Faturamento - {ano_selecionado}")
                    df_display["Data"] = df_display["Data"].dt.strftime("%d/%m/%Y")
                    st.dataframe(df_display[['Data', 'Grupo de Receita', 'Total de Faturamento']])           
                # Criar gráfico de linha com Plotly
                st.subheader(f"Gráfico de Linhas - Faturamento Diário - {ano_selecionado}")
                fig = px.line(df_display, x='Data', y='Total Faturamento',
                            markers=True,
                            color='Grupo de Receita',
                            title='Total de Faturamento por Data')
                # Exibir gráfico no Streamlit
                st.plotly_chart(fig)
                # Criar gráfico de área empilhada
                fig = px.area(
                    df_display,
                    x='Data',
                    y='Total Faturamento',
                    color='Grupo de Receita',  
                    title='Total de Faturamento por Data '
                )
                st.subheader("Faturamento Diário - Gráfico de Áreas Empilhadas")
                st.plotly_chart(fig)
            else:
                #st.info('Por Favor selecionar o filtro e a data!!!', icon='👉')
                #st.info('No canto inferior esquerdo da Tela', icon='👍') 
                st.toast('Por Favor selecionar o filtro e a data!!!')
                st.toast('No canto inferior esquerdo da Tela') 
        conn.close()
        print("Conexão encerrada com sucesso.")
    else:
        st.error("Não foi possivel conectar ao banco de dados.")        

