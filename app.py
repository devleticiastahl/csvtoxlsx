import streamlit as st
import pandas as pd
from io import BytesIO
import chardet

def detect_delimiter_and_encoding(uploaded_file):
    """Detecta automaticamente delimitador e encoding do arquivo"""
    content = uploaded_file.read()
    uploaded_file.seek(0)
    
    encoding = chardet.detect(content)['encoding']
    first_line = content.decode(encoding).split('\n')[0]
    delimiters = [',', ';', '\t', '|']
    delimiter_counts = {delim: first_line.count(delim) for delim in delimiters}
    return max(delimiter_counts, key=delimiter_counts.get), encoding

def convert_csv_to_xlsx(uploaded_file, delimiter=None, encoding=None):
    """Converte CSV para XLSX com tratamento robusto de erros"""
    try:
        if delimiter is None or encoding is None:
            delimiter, encoding = detect_delimiter_and_encoding(uploaded_file)
            st.info(f"Detectado: delimitador '{delimiter}', encoding {encoding}")
        
        df = pd.read_csv(
            uploaded_file,
            delimiter=delimiter,
            encoding=encoding,
            engine='python',
            on_bad_lines='warn',
            thousands=',',
            decimal='.'
        )
        
        if df.empty:
            raise ValueError("Arquivo CSV vazio ou sem dados válidos.")
            
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        return output.getvalue(), df.shape, None
    except Exception as e:
        return None, None, str(e)

def main():
    st.title("📊 Conversor de CSV para XLSX")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv", "txt"])
    
    with st.expander("Opções avançadas"):
        delimiter = st.text_input("Delimitador (deixe em branco para auto-detecção)", value=",")
        encoding = st.text_input("Encoding (deixe em branco para auto-detecção)", value="utf-8")
    
    if uploaded_file is not None:
        st.success("Arquivo carregado!")
        
        try:
            detected_delim, detected_enc = detect_delimiter_and_encoding(uploaded_file)
            uploaded_file.seek(0)
            
            df_preview = pd.read_csv(
                uploaded_file,
                delimiter=delimiter if delimiter else detected_delim,
                encoding=encoding if encoding else detected_enc,
                engine='python',
                nrows=5
            )
            st.dataframe(df_preview)
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Erro ao ler: {e}")
            return
        
        if st.button("Converter para XLSX"):
            with st.spinner("Convertendo..."):
                xlsx_data, shape, error = convert_csv_to_xlsx(
                    uploaded_file,
                    delimiter if delimiter else None,
                    encoding if encoding else None
                )
                
                if error:
                    st.error(f"Erro: {error}")
                else:
                    suggested_name = uploaded_file.name.replace('.csv', '.xlsx').replace('.txt', '.xlsx')
                    st.download_button(
                        "Baixar XLSX",
                        data=xlsx_data,
                        file_name=suggested_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

if __name__ == "__main__":
    main()
