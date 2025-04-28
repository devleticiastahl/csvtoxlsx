import streamlit as st
import pandas as pd
from io import BytesIO
import time

st.set_page_config(
    page_title="Conversor CSV para XLSX",
    page_icon=":bar_chart:",
    layout="centered"
)

def convert_csv_to_xlsx(uploaded_file, delimiter=','):
    try:
        df = pd.read_csv(uploaded_file, delimiter=delimiter)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        return output.getvalue(), df.shape, None
    except Exception as e:
        return None, None, str(e)

def main():
    st.title("📊 Conversor de CSV para XLSX")
    st.markdown("""
    Faça upload de um arquivo CSV e converta para o formato XLSX (Excel) facilmente!
    """)
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo CSV", 
        type=["csv", "txt"],
        accept_multiple_files=False
    )
    
    with st.expander("Opções avançadas"):
        delimiter = st.text_input("Delimitador (padrão é vírgula)", value=",")
        st.caption("Use '\\t' para tabulação ou outro caractere como delimitador.")
    
    if uploaded_file is not None:
        st.success("Arquivo carregado com sucesso!")
      
        st.subheader("Prévia dos dados")
        try:
            df_preview = pd.read_csv(uploaded_file, delimiter=delimiter)
            st.dataframe(df_preview.head())
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return
        
        if st.button("Converter para XLSX"):
            with st.spinner("Convertendo..."):
                xlsx_data, shape, error = convert_csv_to_xlsx(uploaded_file, delimiter)
                
                if error:
                    st.error(f"Erro na conversão: {error}")
                else:
                    st.success("Conversão concluída com sucesso!")
                    st.info(f"Arquivo convertido com {shape[0]} linhas e {shape[1]} colunas.")
                    
                    
                    suggested_name = uploaded_file.name.replace('.csv', '.xlsx').replace('.txt', '.xlsx')
                    
                    
                    st.download_button(
                        label="Baixar arquivo XLSX",
                        data=xlsx_data,
                        file_name=suggested_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

if __name__ == "__main__":
    main()
