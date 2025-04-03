import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard CEVAXIN", layout="wide")
st.title("📊 Dashboard CEVAXIN")

st.markdown("#### Vista pública del dashboard")
st.info("Esta es una vista de solo lectura. La funcionalidad de carga de archivos está desactivada.")

# Leer archivos precargados desde datos_fijos
st.subheader("📁 Reporte automático más reciente")

try:
    files = os.listdir("datos_fijos")
    files = [f for f in files if f.endswith(".xlsx")]
    
    if files:
        latest_file = sorted(files)[-1]
        df = pd.read_excel(f"datos_fijos/{latest_file}")

        st.success(f"Mostrando reporte: **{latest_file}**")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No se encontraron archivos .xlsx en la carpeta `datos_fijos`.")
except Exception as e:
    st.error(f"Ocurrió un error al leer los archivos: {e}")
