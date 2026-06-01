import streamlit as st
import login
import pandas as pd
import locale
import time
import plotly.express as px
from pages.sql_conn import create_connection, fetch_faturamento_data, fetch_faturamentoAtualAnter_data

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
            df_dis = fetch_faturamentoAtualAnter_data(conn, ano_selecionado)
            # Transformar DataFrame em lista de dicionários
            df_dis = df_dis.to_dict('records')
            # Separar os dados por ano
            data_atual = [item for item in df_dis if item["ano"] == ano_selecionado]
            data_anter = [item for item in df_dis if item["ano"] == ano_selecionado-1]
            st.subheader("Comparação dos 4 melhores Itens de Receita")

            # Verificar se há dados suficientes para o ano atual
            if len(data_atual) < 4:
                st.warning(f"Não há dados suficientes para exibir os 4 melhores itens de receita no ano {ano_selecionado}.")
            else:
                for i in range(4):
                    item_atual = data_atual[i]
                    if i < len(data_anter):
                        item_anter = data_anter[i]
                        delta = item_atual["total_vl_total_nf"] - item_anter["total_vl_total_nf"]
                        delta_porcentual = (delta / item_anter['total_vl_total_nf']) * 100 if item_anter['total_vl_total_nf'] != 0 else 0
                    else:
                        # Se não houver dados para o ano anterior, definir delta como None
                        item_anter = {'total_vl_total_nf': 0}
                        delta = None
                        delta_porcentual = None
                    col1, col2 = st.columns(2)
                    with col1:
                        # Verificar se o ano anterior está vazio    
                        if item_anter['total_vl_total_nf'] != 0 and delta is not None:
                            st.metric(
                                label=f"{item_atual['nm_itens_grupo_receita']}",
                                value=f"{item_atual['total_vl_total_nf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if item_atual is not None else "R$ 0",
                                delta=f"{delta:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                delta_color="normal")
                        else:
                            st.metric(
                                label=f"{item_atual['nm_itens_grupo_receita']}",
                                value=f"{item_atual['total_vl_total_nf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if item_atual is not None else "R$ 0",
                                delta=None,                                                              
                                delta_color="normal",
                                help="Não há dados disponíveis para o ano anterior.")
                    with col2:
                        if item_anter['total_vl_total_nf'] != 0 and delta_porcentual is not None:
                            st.metric(
                                label="Variação Percentual",
                                value=f"{delta_porcentual:.2f}%".replace(".", ","),                
                                delta=None,        
                                delta_color="normal",
                                help="O Porcentual do ano anterior")
                        else:
                            st.metric(
                                label="Variação Percentual",
                                value="0.00%",  # Ou uma mensagem como "N/A"
                                delta=None,
                                delta_color="normal",
                                help="Não há dados disponíveis para o ano anterior.")    
                st.subheader("Tabelas e Gráficos do Banco de Dados")
                # Configurar as guias
                guia_tabela, guia_grafico,  guia_graficopie= st.tabs(["📊 Tabela", "📈 Gráfico de Barra", "🥧 Gráfico da Pizza" ])       
                df_display = fetch_faturamento_data(conn, ano_selecionado)    
                df_display['Total de Faturamento'] = df_display['total_vl_total_nf'].apply(
                    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                # Renomeiar as colunas
                df_display = df_display.rename(columns={
                    'fb_id_itens_grupo_receita': 'Item do Grupo',
                    'nm_itens_grupo_receita': 'Nome do Grupo',
                    'total_vl_total_nf': 'Total Faturamento'
                })
                with guia_tabela: 
                    if st.checkbox("Mostrar a Tabela de Faturamento Bruto"):
                        st.subheader(f" 📋 Listagem de Faturamento Bruto - {ano_selecionado}")
                        st.dataframe(
                            df_display[['Item do Grupo', 'Nome do Grupo', 'Total de Faturamento']])
                    # Filtro de Grupos (MultiSelect)
                    st.sidebar.header("📦 Filtrar os Grupos")
                    df = df_display.sort_values("Total Faturamento")
                    grupos = st.sidebar.multiselect(
                        "Selecione o(s) Grupo(s):",
                        options=df["Nome do Grupo"].unique(),
                        default=df["Nome do Grupo"].unique())           
                    # Filtrar o(s) Grupo(s)
                    if grupos:
                        df = df[df["Nome do Grupo"].isin(grupos)]
                    # Agrupar por Grupo e somar as Total Faturamento
                    pro_quant = df.groupby("Nome do Grupo")["Total Faturamento"].sum().reset_index()
                    # Ordenar pela coluna Total Faturamento
                    pro_quant = pro_quant.sort_values(by="Total Faturamento", ascending=True)
                with guia_grafico:     
                    # Criar o gráfico horizontal de Faturamento por tipo do Grupo",
                    st.subheader(f"Gráfico de Barra em {ano_selecionado}")
                    fig_quant = px.bar(
                        pro_quant, x="Total Faturamento", y="Nome do Grupo",
                        title=" 📈 Total de Grupo de Receita",
                        labels={"Nome do Grupo": "Grupo",
                                "Total Faturamento": "Total da Receita"},
                        color="Nome do Grupo",
                        orientation="h")
                    # Mostrar Graficos
                    st.plotly_chart(fig_quant, use_container_width=True)
                with guia_graficopie: 
                    st.subheader(f"Gráfico de Pizza em {ano_selecionado}")
                    df['porcentagem'] = (df["Total Faturamento"] /
                                        df["Total Faturamento"].sum()) * 100
                    threshold = 8  # então, se for menor que 8% vão entrar no Grupo
                    outros = df[df['porcentagem'] < threshold].sum(numeric_only=True)
                    outros_label = pd.DataFrame({
                        'Nome do Grupo': ['Outros'],
                        'Total Faturamento': [outros['Total Faturamento']],
                        'porcentagem': [outros['porcentagem']]
                        })
                    df_maiores = df[df['porcentagem'] >= threshold]
                    df_final = pd.concat([df_maiores, outros_label], ignore_index=True)
                    # Criar gráfico de pizza com Plotly
                    fig = px.pie(
                        df_final,
                        names='Nome do Grupo',
                        values='Total Faturamento',
                        title="  Grupos de Receita em Porcentagem",
                        hole=0.3,
                    )
                    st.plotly_chart(fig)
        conn.close()
        print("Conexão encerrada com sucesso.")
    else:
        st.error("Não foi possivel conectar ao banco de dados.")
