import streamlit as st
import login
import pandas as pd
import time
import plotly.express as px
from pages.sql_conn import create_connection, fetch_clientes_data, fetch_clienteAtualAnter_data

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
            df_dis = fetch_clienteAtualAnter_data(conn, ano_selecionado)

            # Verificar se existem dados para o ano selecionado e o ano anterior
            dados_atual = df_dis[df_dis['ano'] == ano_selecionado].iloc[0] if not df_dis[df_dis['ano'] == ano_selecionado].empty else None
            dados_anter = df_dis[df_dis['ano'] == ano_selecionado - 1].iloc[0] if not df_dis[df_dis['ano'] == ano_selecionado - 1].empty else None

            # Definir valores padrão caso não haja dados para o ano anterior
            if dados_anter is None:
                dados_anter = { 'quantidade_clientes': 0, 'subtotal': 0}

            # Calcular os deltas (diferenças)
            if dados_atual is not None:
                delta_clientes = dados_atual['quantidade_clientes'] - dados_anter['quantidade_clientes']
                delta_porcentualCliente = (
                    (dados_atual['quantidade_clientes'] - dados_anter['quantidade_clientes']) / dados_anter['quantidade_clientes']) * 100 if dados_anter['quantidade_clientes'] != 0 else 0
                delta_faturamento = dados_atual['subtotal'] - dados_anter['subtotal']
                delta_porcentual = (
                    (dados_atual['subtotal'] - dados_anter['subtotal']) / dados_anter['subtotal']) * 100 if dados_anter['subtotal'] != 0 else 0
            else:
                # Caso não haja dados para o ano selecionado
                delta_clientes = 0
                delta_porcentualCliente = 0
                delta_faturamento = 0
                delta_porcentual = 0

            st.subheader(f"Comparação do Ano {ano_selecionado} e {ano_selecionado - 1}")
            col1, col2 = st.columns(2)
            with col1:
                # Verificar se o ano anterior está vazio
                if dados_anter is not None and dados_anter['subtotal'] != 0:
                    st.metric(
                        label="Total de Faturamento",
                        value=f"{dados_atual['subtotal']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if dados_atual is not None else "R$ 0",
                        delta=f"{delta_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        delta_color="normal",
                        help="Comparando as diferenças de Faturamento do ano anterior")
                else:
                    st.metric(
                        label="Total de Faturamento",                        
                        value=f"{dados_atual['subtotal']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if dados_atual is not None else "R$ 0",
                        delta=None,
                        delta_color="normal",
                        help="Não há dados disponíveis para o ano anterior.")
            with col2:
                st.metric(
                    label="Variação Percentual do Faturamento",
                    value=f"{delta_porcentual:.2f}%".replace(".", ","),
                    delta=None,
                    delta_color="normal",
                    help="O Porcentual do ano anterior.")
            col3, col4 = st.columns(2)
            with col3:
                if dados_anter is not None and dados_anter['subtotal'] != 0:
                    st.metric(
                        label="Quantidades de Clientes",
                        value=f"{int(dados_atual['quantidade_clientes']):,}".replace(",", ".") if dados_atual is not None else "0",
                        delta=f"{int(delta_clientes):,}".replace(",", "."),
                        delta_color="normal",
                        help="Comparando as diferenças das quantidade de Clientes do ano anterior.")
                else:   
                    st.metric(
                        label="Quantidades de Clientes",
                        value=f"{int(dados_atual['quantidade_clientes']):,}".replace(",", ".") if dados_atual is not None else "0",
                        delta=None,
                        delta_color="normal",
                        help="Não há dados disponíveis para o ano anterior.")
            with col4:
                st.metric(
                    label="Variação Percentual dos Clientes",
                    value=f"{delta_porcentualCliente:.2f}%".replace(".", ","),
                    delta=None,
                    delta_color="normal",
                    help="O Porcentual do ano anterior." )

            st.subheader("Tabelas e Gráficos do Banco de Dados")
            df_display = fetch_clientes_data(conn, ano_selecionado)
            df_display['total_vl_total_nf'] = pd.to_numeric(df_display['total_vl_total_nf'], errors='coerce')
            df_display['Total de Faturamento'] = df_display['total_vl_total_nf'].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            df_display = df_display.rename(columns={
                'nm_Cliente': 'Nome do Cliente',
                'total_vl_total_nf': 'Total Faturamento'
            })
            # Configurar as guias
            guia_tabela, guia_grafico = st.tabs(["📊 Tabela", "📈 Gráfico"])
            # Guia de tabela
            with guia_tabela:
                st.subheader(f" 🥇 Listagem dos 10 Top Clientes em {ano_selecionado}")       
                st.dataframe(
                    df_display[['Nome do Cliente', 'Total de Faturamento']])
            # Guia de gráfico
            with guia_grafico:
                st.subheader(f" 🥇 Os 10 TOP dos Clientes em {ano_selecionado}")
                # Criar o gráfico horizontal
                pro_quant = df_display.groupby("Nome do Cliente")[
                    "Total Faturamento"].sum().reset_index()
                pro_quant = pro_quant.sort_values(
                    by="Total Faturamento", ascending=True)
                pro_quant['Total Faturamento'] = pd.to_numeric(
                    pro_quant['Total Faturamento'], errors='coerce')
                pro_quant = pro_quant.nlargest(10, 'Total Faturamento')

                def encurtar_nome(nome, max_length=30):
                    return nome if len(nome) <= max_length else nome[:max_length] + "..."
                # Encurtar nomes dos clientes
                pro_quant['Nome do Cliente'] = pro_quant['Nome do Cliente'].apply(
                    lambda x: encurtar_nome(x, max_length=30))
                # Ajustar valores para serem exibidos em milhares no gráfico
                pro_quant['Total Faturamento (Milhares)'] = pro_quant['Total Faturamento'] / 1000
                fig_quant = px.bar(
                    pro_quant, x="Total Faturamento", y="Nome do Cliente",
                    labels={"Nome do Cliente": "Nomes",
                            "Total Faturamento": "Faturamento (em Milhares - R$)"},
                    color="Nome do Cliente",
                    orientation="h")
                # Ajustar layout do gráfico
                fig_quant.update_layout(
                    height=600,
                    margin=dict(l=150, r=20, t=50, b=20),
                )
                fig_quant.update_yaxes(categoryorder="total descending")
                st.plotly_chart(fig_quant, use_container_width=True)
        conn.close()
        print("Conexão encerrada com sucesso.")
    else:
        st.error("Não foi possivel conectar ao banco de dados.")
