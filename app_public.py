import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils_dashboard import (
    cargar_datos_excel,
    generar_graficos_por_dia,
    generar_graficos_por_sede,
    generar_graficos_globales,
    mostrar_conclusiones,
    mostrar_indicadores_gestion
)

st.set_page_config(page_title="Dashboard CEVAXIN", layout="wide")
st.title("📊 Dashboard CEVAXIN")

st.markdown("#### Vista pública del dashboard (solo lectura)")
st.info("Esta es una vista sin opción para cargar archivos. Muestra únicamente reportes procesados previamente.")

# Directorio de datos precargados
directorio = "datos_fijos"

# Obtener lista de archivos disponibles
archivos_disponibles = sorted([f for f in os.listdir(directorio) if f.endswith(".xlsx")])
fechas_disponibles = [datetime.strptime(f.split(".")[0], "%d%b%Y_%Z") for f in archivos_disponibles]

# Selección de fecha con calendario
fecha_seleccionada = st.date_input("📅 Selecciona una fecha", value=max(fechas_disponibles).date(), min_value=min(fechas_disponibles).date(), max_value=max(fechas_disponibles).date())

# Convertir a formato archivo
archivo_actual = f"{fecha_seleccionada.strftime('%d%b%Y')}_CHORRERA.xlsx"

if archivo_actual in archivos_disponibles:
    ruta_archivo = os.path.join(directorio, archivo_actual)
    datos = cargar_datos_excel(ruta_archivo)

    # Mostrar tablas y gráficos
    with st.expander("📄 Tabla de entradas por servicio"):
        st.dataframe(datos)

    st.markdown("---")
    generar_graficos_por_dia(datos)
    mostrar_conclusiones(datos, modo="día")

    st.markdown("---")
    generar_graficos_por_sede(datos)
    mostrar_conclusiones(datos, modo="sede")

    st.markdown("---")
    generar_graficos_globales(datos)
    mostrar_conclusiones(datos, modo="global")

    st.markdown("---")
    mostrar_indicadores_gestion(datos)

else:
    st.warning("No hay reportes disponibles para la fecha seleccionada.")
