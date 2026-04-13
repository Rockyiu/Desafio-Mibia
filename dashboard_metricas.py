import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Dashboard RPA", layout="wide")
st.title("🤖 Monitoramento RPA - MIBIA Digital")

# Conecta ao banco e lê os dados
conn = sqlite3.connect('rpa_log.db')
df = pd.read_sql_query("SELECT * FROM logs ORDER BY data_hora DESC", conn)

if not df.empty:
    # LÓGICA PARA EXIBIR A INDICAÇÃO DE ONDE FOI SALVO (Requisito 4)
    def indicar_caminho(nome_arquivo):
        if not nome_arquivo or nome_arquivo == "N/A":
            return "Não salvo (Erro)"
        
        # Mapeia a pasta com base no nome do arquivo gerado
        if "NFE" in nome_arquivo:
            return f"📂 /uploads/XML/{nome_arquivo}"
        elif "NF_Servico" in nome_arquivo:
            return f"📂 /uploads/NF/{nome_arquivo}"
        elif "Extrato" in nome_arquivo:
            return f"📂 /uploads/Extratos/{nome_arquivo}"
        else:
            return f"📂 /uploads/NF/{nome_arquivo}"

    # Adiciona a nova coluna no DataFrame visual
    df['Indicação de Destino'] = df['arquivo_novo'].apply(indicar_caminho)

    # Mostra métricas rápidas no topo
    col1, col2 = st.columns(2)
    col1.metric("Total Processados", len(df))
    col2.metric("Total de Erros", len(df[df['status'] == 'Erro']))

    # Reorganiza a ordem das colunas para ficar mais bonito na tela
    colunas_exibir = ['id', 'arquivo_original', 'arquivo_novo', 'Indicação de Destino', 'status', 'data_hora', 'mensagem_erro']
    
    # Mostra a tabela de dados
    st.dataframe(df[colunas_exibir], use_container_width=True, hide_index=True)
else:
    st.info("⚠️ Nenhum arquivo processado ainda. Rode o robô no Terminal!")