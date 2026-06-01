import pyodbc
import pandas as pd

def create_connection():
    try:
        # Configuração da conexão
        db_config = {          
            'driver': 'ODBC Driver 17 for SQL Server',
            'server': '********', 
            'database': '********',  
            'username': '********',  
            'password': '********', 
        }
        # Criar a string de conexão
        conn_str = (
            f"DRIVER={{{db_config['driver']}}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
        )
        # Conectar ao banco de dados e executar a query
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"Erro ao conectar ao Banco: {e}")
        return None

def fetch_ano(conn):
    query = """SELECT DISTINCT FORMAT(dl.dt_lancamento, 'yyyy') AS ano
                FROM ********DW.DW.DDataLancamento dl 
                ORDER BY ano;"""
    return pd.read_sql_query(query, conn)

def fetch_faturamento_data(conn, ano):
    # Lista cada Grupo de Receita com o total por Ano 
    query = """SELECT fb.id_itens_grupo_receita AS fb_id_itens_grupo_receita, 
                    dgr.nm_itens_grupo_receita AS nm_itens_grupo_receita, SUM(fb.vl_total_nf) AS total_vl_total_nf
                FROM ********DW.DW.FFaturamentoBruto fb
                JOIN ********DW.DW.DItensGrupoReceita dgr 
                    ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                JOIN ********DW.DW.DDataLancamento ddl
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
                WHERE YEAR(ddl.dt_lancamento) = ?    
                GROUP BY fb.id_itens_grupo_receita, dgr.nm_itens_grupo_receita
                HAVING SUM(fb.vl_total_nf) > 0
                ORDER BY total_vl_total_nf DESC;"""    
    return pd.read_sql_query(query, conn, params=[ano])

def fetch_clientes_data(conn, ano):
    query = """SELECT TOP 10 cl.nm_Cliente, dgr.nm_itens_grupo_receita, SUM(fb.vl_total_nf) AS total_vl_total_nf
            	FROM ********DW.DW.DCliente cl
	            JOIN ********DW.DW.FFaturamentoBruto fb
        		    ON cl.id_cliente = fb.id_cliente
            	JOIN ********DW.DW.DDataLancamento ddl
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
            	JOIN ********DW.DW.DItensGrupoReceita dgr 
            		ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita         
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY cl.nm_Cliente, dgr.nm_itens_grupo_receita
                ORDER By total_vl_total_nf DESC;"""
    return pd.read_sql_query(query, conn, params=[ano])

def fetch_evolucao_data(conn, ano):
    # Lista o Faturamento Bruto Total por mes em ano 
    query = """SELECT MONTH(ddl.dt_lancamento) AS numero_mes,
                FORMAT(ddl.dt_lancamento, 'MMMM') AS nome_mes, 
                SUM(fb.vl_total_nf) AS total_vl_total_nf
                FROM ********DW.DW.FFaturamentoBruto fb
                JOIN ********DW.DW.DItensGrupoReceita dgr 
                    ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                JOIN ********DW.DW.DDataLancamento ddl
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY MONTH(ddl.dt_lancamento), FORMAT(ddl.dt_lancamento, 'MMMM')
                HAVING SUM(fb.vl_total_nf) > 0
                ORDER BY MONTH(ddl.dt_lancamento);"""
    return pd.read_sql_query(query, conn, params=[ano])

def fetch_clientereceita_data(conn, ano):
    query = """WITH RankedClientes AS (
               SELECT cl.nm_Cliente, dgr.id_itens_grupo_receita,
                    dgr.nm_itens_grupo_receita, SUM(fb.vl_total_nf) AS total_vl_total_nf,
                    ROW_NUMBER() OVER (PARTITION BY dgr.id_itens_grupo_receita 
                    ORDER BY SUM(fb.vl_total_nf) DESC) AS rank
                FROM ********DW.DW.DCliente cl
                JOIN ********DW.DW.FFaturamentoBruto fb 
                    ON cl.id_cliente = fb.id_cliente
                JOIN ********DW.DW.DDataLancamento ddl 
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
                JOIN ********DW.DW.DItensGrupoReceita dgr  
                    ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY cl.nm_Cliente, dgr.id_itens_grupo_receita, dgr.nm_itens_grupo_receita
                HAVING SUM(fb.vl_total_nf) > 0)
               SELECT id_itens_grupo_receita, nm_itens_grupo_receita, nm_Cliente, total_vl_total_nf
                FROM RankedClientes
                WHERE rank <= 10 
                ORDER BY total_vl_total_nf DESC, nm_itens_grupo_receita;"""
    return pd.read_sql_query(query, conn, params=[ano])

def fetch_mensalfaturamento_data(conn, ano):
        # Lista de Grupo de Receita por Mes em ano  
        query ="""SELECT 
                    dgr.nm_itens_grupo_receita AS nm_itens_grupo_receita,
                    DATENAME(MONTH, ddl.dt_lancamento) AS num_mes, 
                    MONTH(ddl.dt_lancamento) AS ordem_mes, 
                    SUM(fb.vl_total_nf) AS total_vl_total_nf
                FROM ********DW.DW.FFaturamentoBruto fb
                JOIN ********DW.DW.DItensGrupoReceita dgr  
                    ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                JOIN ********DW.DW.DDataLancamento ddl 
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY dgr.nm_itens_grupo_receita, DATENAME(MONTH, ddl.dt_lancamento), MONTH(ddl.dt_lancamento)
                HAVING SUM(fb.vl_total_nf) > 0
                ORDER BY ordem_mes, dgr.nm_itens_grupo_receita, total_vl_total_nf DESC;"""
        return pd.read_sql_query(query, conn, params=[ano])

'''
anterior
MONTH(ddl.dt_lancamento) AS num_mes,

def fetch_mensalfaturamento_data(conn, ano):
    # Lista de Grupo de Receita por Mes em ano  
    query ="""SELECT dgr.nm_itens_grupo_receita AS nm_itens_grupo_receita,
                    FORMAT(ddl.dt_lancamento, 'MMMM') AS nome_mes,
                    SUM(fb.vl_total_nf) AS total_vl_total_nf
                FROM ********DW.DW.FFaturamentoBruto fb
                JOIN ********DW.DW.DItensGrupoReceita dgr 
                    ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                JOIN ********DW.DW.DDataLancamento ddl
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY dgr.nm_itens_grupo_receita, FORMAT(ddl.dt_lancamento, 'MMMM'), MONTH(ddl.dt_lancamento)
                HAVING SUM(fb.vl_total_nf) > 0
                ORDER BY MONTH(ddl.dt_lancamento), dgr.nm_itens_grupo_receita, total_vl_total_nf DESC;"""
    return pd.read_sql_query(query, conn, params=[ano])
'''

def fetch_clienteAtualAnter_data(conn, ano):
    # Calcular a quantidade do clientes e faturamentos no ano Atual e Anterior  
    query ="""SELECT YEAR(ddl.dt_lancamento) AS ano, COUNT(DISTINCT cl.nm_Cliente) AS quantidade_clientes,
                    SUM(fb.vl_total_nf) AS subtotal
                FROM ********DW.DW.DCliente cl
                JOIN ********DW.DW.FFaturamentoBruto fb 
                    ON cl.id_cliente = fb.id_cliente   
                JOIN ********DW.DW.DDataLancamento ddl
                    ON fb.id_data_lancamento = ddl.id_data_lancamento   
                WHERE YEAR(ddl.dt_lancamento) BETWEEN ? -1 AND ?
                GROUP BY YEAR(ddl.dt_lancamento)
                ORDER BY ano;"""
    return pd.read_sql_query(query, conn, params=[ano, ano])

def fetch_faturamentoAtualAnter_data(conn, ano):
    # Calcular a quantidade do faturamentos com receitas no ano Atual e Anterior       
    query ="""WITH ranked_results AS (
                SELECT YEAR(ddl.dt_lancamento) AS ano, fb.id_itens_grupo_receita AS fb_id_itens_grupo_receita,
                    dgr.nm_itens_grupo_receita AS nm_itens_grupo_receita, SUM(fb.vl_total_nf) AS total_vl_total_nf,
                    ROW_NUMBER() OVER (PARTITION BY YEAR(ddl.dt_lancamento) ORDER BY SUM(fb.vl_total_nf) DESC) AS rn
                  FROM ********DW.DW.FFaturamentoBruto fb
                  JOIN ********DW.DW.DItensGrupoReceita dgr
                      ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                  JOIN ********DW.DW.DDataLancamento ddl 
                      ON fb.id_data_lancamento = ddl.id_data_lancamento
                  WHERE YEAR(ddl.dt_lancamento) BETWEEN ? -1 AND ?
                  GROUP BY YEAR(ddl.dt_lancamento), fb.id_itens_grupo_receita, dgr.nm_itens_grupo_receita)
                SELECT *
                    FROM ranked_results
                    WHERE rn <= 4
                    ORDER BY ano DESC;"""
    return pd.read_sql_query(query, conn, params=[ano, ano])
    
def fetch_receitaliquidaAtual_data(conn, ano):
    # Calcular a receita liquida do ano de cada grupo de receitas  
    query ="""SELECT fb.id_itens_grupo_receita AS fb_id_itens_grupo_receita, dgr.nm_itens_grupo_receita AS nm_itens_grupo_receita, 
                SUM(fb.vl_total_nf) AS total_vl_total_nf, SUM(fb.vl_liquido) AS total_vl_liquido,
            (   SELECT COALESCE(SUM(dv.vl_liquido), 0)
                    FROM ********DW.DW.FDevolucoesVendas dv
                    JOIN ********DW.DW.DDataLancamento ddl_dv
                        ON dv.id_data_lancamento = ddl_dv.id_data_lancamento
                    WHERE dv.id_itens_grupo_receita = fb.id_itens_grupo_receita
                        AND YEAR(ddl_dv.dt_lancamento) = ?
            ) AS total_vl_devolucoesvendas,
            (   SELECT COALESCE(SUM(ds.vl_total_cr), 0)
                    FROM ********DW.DW.FDevolucoesServicos ds
                    JOIN ********DW.DW.DDataLancamento ddl_ds
                        ON ds.id_data_lancamento = ddl_ds.id_data_lancamento
                    WHERE ds.id_itens_grupo_receita = fb.id_itens_grupo_receita
                        AND YEAR(ddl_ds.dt_lancamento) = ?
            ) AS total_vl_devolucoesservicos, SUM(fb.vl_liquido) - 
            (   SELECT COALESCE(SUM(dv.vl_liquido), 0)
                    FROM ********DW.DW.FDevolucoesVendas dv
                    JOIN ********DW.DW.DDataLancamento ddl_dv
                        ON dv.id_data_lancamento = ddl_dv.id_data_lancamento
                    WHERE dv.id_itens_grupo_receita = fb.id_itens_grupo_receita
                        AND YEAR(ddl_dv.dt_lancamento) = ?
            ) - 
            (   SELECT COALESCE(SUM(ds.vl_total_cr), 0)
                    FROM ********DW.DW.FDevolucoesServicos ds
                    JOIN ********DW.DW.DDataLancamento ddl_ds
                        ON ds.id_data_lancamento = ddl_ds.id_data_lancamento
                    WHERE ds.id_itens_grupo_receita = fb.id_itens_grupo_receita
                        AND YEAR(ddl_ds.dt_lancamento) = ?
            ) AS receita_liquida
                FROM ********DW.DW.FFaturamentoBruto fb
                JOIN ********DW.DW.DItensGrupoReceita dgr 
                        ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                JOIN ********DW.DW.DDataLancamento ddl
                        ON fb.id_data_lancamento = ddl.id_data_lancamento
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY 
                    fb.id_itens_grupo_receita, 
                    dgr.nm_itens_grupo_receita
                HAVING 
                    SUM(fb.vl_total_nf) > 0
                ORDER BY receita_liquida DESC;"""
    params = [ano, ano, ano, ano, ano]
    return pd.read_sql_query(query, conn, params=params) 
   

def fetch_diariofaturamento_data(conn, ano):
    # Lista de Grupo de Receita por Dia em ano 
    query ="""SELECT dgr.nm_itens_grupo_receita AS nm_itens_grupo_receita, 	    
                    CAST(ddl.dt_lancamento AS DATE) AS dt_lancamento,
                    SUM(fb.vl_total_nf) AS total_vl_total_nf
                FROM ********DW.DW.FFaturamentoBruto fb
                JOIN ********DW.DW.DItensGrupoReceita dgr 
                    ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                JOIN ********DW.DW.DDataLancamento ddl
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY dgr.nm_itens_grupo_receita, ddl.dt_lancamento
                HAVING SUM(fb.vl_total_nf) > 0
                ORDER BY dgr.nm_itens_grupo_receita, ddl.dt_lancamento;"""
    return pd.read_sql_query(query, conn, params=[ano])

def fetch_diarioportugues_data(conn, ano):
    query ="""SELECT dgr.nm_itens_grupo_receita AS nm_itens_grupo_receita, 	    
                    CONVERT(VARCHAR, ddl.dt_lancamento, 103) AS dt_lancamento,
                    SUM(fb.vl_total_nf) AS total_vl_total_nf
                FROM ********DW.DW.FFaturamentoBruto fb
                JOIN ********DW.DW.DItensGrupoReceita dgr 
                    ON fb.id_itens_grupo_receita = dgr.id_itens_grupo_receita
                JOIN ********DW.DW.DDataLancamento ddl
                    ON fb.id_data_lancamento = ddl.id_data_lancamento
                WHERE YEAR(ddl.dt_lancamento) = ?
                GROUP BY dgr.nm_itens_grupo_receita, ddl.dt_lancamento
                HAVING SUM(fb.vl_total_nf) > 0
                ORDER BY dgr.nm_itens_grupo_receita, ddl.dt_lancamento;"""
    return pd.read_sql_query(query, conn, params=[ano])
