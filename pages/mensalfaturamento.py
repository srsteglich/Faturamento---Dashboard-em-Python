import streamlit as st
import login
import time
import plotly.express as px
from pages.sql_conn import create_connection, fetch_mensalfaturamento_data

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
            df_display = fetch_mensalfaturamento_data(conn, ano_selecionado)
            meses_portugues = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março",
                4: "Abril", 5: "Maio", 6: "Junho",
                7: "Julho", 8: "Agosto", 9: "Setembro",
                10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }                           
            df_display['Mês'] = df_display['ordem_mes'].map(meses_portugues)
            df_display['Total de Faturamento'] = df_display['total_vl_total_nf'].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            df_display = df_display.rename(columns={'nm_itens_grupo_receita': 'Grupo de Receita',
                                                    'total_vl_total_nf': 'Total Faturamento'})

            # Ordenação correta
            df_display = df_display.sort_values(by=['ordem_mes', 'Grupo de Receita', 'Total Faturamento'], ascending=[True, True, False])
            # Remover coluna auxiliar para evitar confusão
            df_display = df_display.drop(columns=['ordem_mes'])  
            #st.dataframe(df_display)
            # Filtro de Grupos (MultiSelect)
            st.sidebar.header("📦 Filtrar Grupo de Receita")
            grupos = st.sidebar.multiselect(
                "Selecione Grupo de Receita:",
                options=df_display["Grupo de Receita"].unique())
            if grupos:
                df_display = df_display[df_display["Grupo de Receita"].isin(grupos)]

            # Filtrar Data por Intervalo de Meses por Slider
            st.sidebar.header("📅 Filtrar por Mês")
            meses = list(meses_portugues.values())

            #Selecionar intervalo de meses
            mes_inicio = st.sidebar.selectbox("Mês de Início", options=meses, index=0)
            mes_final = st.sidebar.selectbox("Mês de Fim", options=meses, index=len(meses) - 1)

            meses_dict = {mes: idx for idx, mes in enumerate(meses, start=1)}                                          
            num_mes_inicio = meses_dict[mes_inicio]
            num_mes_final = meses_dict[mes_final]

            # Validar intervalo de meses
            if num_mes_inicio > num_mes_final:
                st.warning("O Mês Inicial não pode ser maior que o Mês Final. Selecione novamente.", icon="⚠️")
            else:
                df_filtrado = df_display[df_display['Mês'].map(meses_dict).between(num_mes_inicio, num_mes_final)]

                if df_filtrado.empty:                
                     st.info("Nenhum dado disponível para o intervalo de meses selecionado.", icon="ℹ️")
                else:
                    st.subheader("Tabelas e Graficos do Banco de dados")
                    # Configurar as guias
                    meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                    guia_tabela, guia_graficoline,  guia_graficoarea= st.tabs(["📊 Tabela", "📈 Gráfico de Linhas", " Gráfico de Area" ])  
                    with guia_tabela: 
                        if st.checkbox("Mostrar a Tabela Mensal do Faturamento"):           
                            st.subheader(f"📋 Listagem mensal de Faturamento - {ano_selecionado}")
                            st.dataframe(df_filtrado[['Mês', 'Grupo de Receita', 'Total de Faturamento']])
                    with guia_graficoline: 
                        st.subheader(f"Gráfico de Linhas - Faturamento - {ano_selecionado}")
                        # Criar gráfico de Linha com Plotly
                        fig = px.line(df_filtrado, x='Mês', y='Total Faturamento',                                  
                                markers=True, color='Grupo de Receita', title='Total de Faturamento por Mês',       
                                category_orders={"Mês": meses_ordem})     
                        st.plotly_chart(fig)
                        #st.dataframe(df_filtrado)
                    with guia_graficoarea: 
                        # Criar gráfico de Área Empilhada
                        st.subheader(f"📉 Gráfico de Área - Faturamento Mensal - {ano_selecionado}")
                        fig = px.area(df_filtrado, x='Mês', y='Total Faturamento',    
                            color='Grupo de Receita', title='Total de Faturamento por Mês',
                            category_orders={"Mês": meses_ordem})          
                        st.plotly_chart(fig)            
        conn.close()
        print("Conexão encerrada com sucesso.")
    else:
        st.error("Não foi possivel conectar ao banco de dados.")