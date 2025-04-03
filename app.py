import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="Dashboard CEVAXIN", layout="wide")
st.title("📊 Dashboard Clínico - CEVAXIN INFORME SEDES")

@st.cache_data
def convertir_tiempo_a_minutos(valor):
    try:
        h, m, s = map(int, str(valor).split(':'))
        return h * 60 + m + s / 60
    except:
        return None

@st.cache_data
def cargar_datos_desde_archivos(carpeta):
    df_total = pd.DataFrame()
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".xlsx"):
            ruta = os.path.join(carpeta, archivo)
            nombre = archivo.replace(".xlsx", "")
            try:
                fecha, sede = nombre.split("_", 1)
            except:
                continue
            try:
                df = pd.read_excel(ruta)
                df["Sede"] = sede.upper()
                df["Fecha"] = fecha.upper()
                df["Tiempo_Espera_min"] = df["Tiempo Promedio Esperando"].apply(convertir_tiempo_a_minutos)
                df["Tiempo_Atencion_min"] = df["Tiempo Promedio Atendiendo"].apply(convertir_tiempo_a_minutos)
                df_total = pd.concat([df_total, df], ignore_index=True)
            except Exception as e:
                st.warning(f"Error leyendo {archivo}: {e}")
    return df_total
# Cargar datos históricos (hasta el 02ABR2025)
df_base = cargar_datos_desde_archivos("datos_fijos")

# Cargar archivos nuevos desde el sidebar
st.sidebar.title("📂 Cargar nuevos archivos")
archivos_nuevos = st.sidebar.file_uploader("Sube archivos Excel (desde 03ABR2025)", type="xlsx", accept_multiple_files=True)

df_nuevo = pd.DataFrame()
if archivos_nuevos:
    for archivo in archivos_nuevos:
        nombre = archivo.name.replace(".xlsx", "")
        try:
            fecha, sede = nombre.split("_", 1)
            df_temp = pd.read_excel(archivo)
            df_temp["Sede"] = sede.upper()
            df_temp["Fecha"] = fecha.upper()
            df_temp["Tiempo_Espera_min"] = df_temp["Tiempo Promedio Esperando"].apply(convertir_tiempo_a_minutos)
            df_temp["Tiempo_Atencion_min"] = df_temp["Tiempo Promedio Atendiendo"].apply(convertir_tiempo_a_minutos)
            df_nuevo = pd.concat([df_nuevo, df_temp], ignore_index=True)
        except Exception as e:
            st.warning(f"Error leyendo {archivo.name}: {e}")

# Unir base + nuevos
df_total = pd.concat([df_base, df_nuevo], ignore_index=True)

# Selección de vista
st.sidebar.title("📊 Vista de Análisis")
modo_vista = st.sidebar.radio("Selecciona vista:", ["Por Sede", "Por Día", "Global"])

# Preparar datos únicos
fechas = sorted(df_total["Fecha"].unique())
sedes = sorted(df_total["Sede"].unique())

# Filtros por sede y fecha
fecha_sel = st.sidebar.selectbox("Selecciona fecha", fechas)
sede_sel = st.sidebar.selectbox("Selecciona sede", sedes)
def mostrar_conclusion(msg):
    st.markdown(f"<div style='font-size:16px; color:#4CAF50;'>💬 {msg}</div>", unsafe_allow_html=True)

def mostrar_grafica_barras(df, x, y, titulo, color="#1f77b4"):
    fig = px.bar(df, x=x, y=y, title=titulo, color_discrete_sequence=[color])
    st.plotly_chart(fig, use_container_width=True)

def mostrar_embudo(df):
    ciclo = [
        "Doc. Consentimiento", "Lectura de consentimiento informado", "mRNA-1403 P301",
        "Laboratorio / Laboratorio Interno", "Aleatorización y Preparación del producto",
        "Vacunación", "App móvil", "Observación postvacunación", "Cierre de visita"
    ]
    servicios = df["Nombre"].unique()
    extras = [s for s in servicios if s not in ciclo]
    orden = ciclo + extras
    funnel_df = df[df["Nombre"].isin(orden)].groupby("Nombre")["Entradas"].sum().reindex(orden).dropna().reset_index()
    fig = px.funnel(funnel_df, x="Entradas", y="Nombre", title="🔻 Embudo Clínico Completo")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_conclusion(f"🔎 Caída total: de {funnel_df['Entradas'].max()} a {funnel_df['Entradas'].min()} en {funnel_df.shape[0]} pasos.")

def mostrar_conclusiones(df):
    if df.empty:
        return
    max_espera = df.groupby("Nombre")["Tiempo_Espera_min"].mean().idxmax()
    max_atencion = df.groupby("Nombre")["Tiempo_Atencion_min"].mean().idxmax()
    sede_finalizados = df.groupby("Sede")["Finalizados"].sum().idxmax()
    servicio_cancelaciones = df.groupby("Nombre")["Cancelados"].sum().idxmax()
    total_cancelados = int(df["Cancelados"].sum())
    st.markdown("### 🧠 Conclusiones Inteligentes")
    st.success(f"🕒 Mayor espera: **{max_espera}**")
    st.success(f"💉 Mayor atención: **{max_atencion}**")
    st.success(f"🏥 Sede con más finalizados: **{sede_finalizados}**")
    st.success(f"📉 Servicio con más cancelaciones: **{servicio_cancelaciones}**")
    st.success(f"❌ Total cancelados: **{total_cancelados}**")
# === Render de visualizaciones ===

if modo_vista == "Por Sede":
    df_view = df_total[(df_total["Fecha"] == fecha_sel) & (df_total["Sede"] == sede_sel)]
    st.header(f"📍 Sede: {sede_sel} | 📅 Fecha: {fecha_sel}")

elif modo_vista == "Por Día":
    df_view = df_total[df_total["Fecha"] == fecha_sel]
    st.header(f"📅 Fecha: {fecha_sel} (Todas las sedes)")

else:  # Global
    df_view = df_total
    st.header("🌍 Vista Global (Todos los días y sedes)")

# === Gráficas principales ===

# Entradas por servicio
entradas = df_view.groupby("Nombre")["Entradas"].sum().reset_index()
mostrar_grafica_barras(entradas, "Nombre", "Entradas", "🎟️ Entradas por Servicio")
mostrar_conclusion(f"Servicio con más entradas: **{entradas.loc[entradas['Entradas'].idxmax(), 'Nombre']}**")

# Tiempo promedio de espera
espera = df_view.groupby("Nombre")["Tiempo_Espera_min"].mean().reset_index()
mostrar_grafica_barras(espera, "Nombre", "Tiempo_Espera_min", "🕒 Tiempo Promedio de Espera (min)")
mostrar_conclusion(f"Mayor tiempo de espera: **{espera.loc[espera['Tiempo_Espera_min'].idxmax(), 'Nombre']}**")

# Tiempo promedio de atención
atencion = df_view.groupby("Nombre")["Tiempo_Atencion_min"].mean().reset_index()
mostrar_grafica_barras(atencion, "Nombre", "Tiempo_Atencion_min", "💉 Tiempo Promedio de Atención (min)")
mostrar_conclusion(f"Mayor tiempo de atención: **{atencion.loc[atencion['Tiempo_Atencion_min'].idxmax(), 'Nombre']}**")

# Embudo clínico
mostrar_embudo(df_view)

# Doc. Consentimiento vs Cancelados por día
if modo_vista == "Global":
    df_dc = df_total[df_total["Nombre"] == "Doc. Consentimiento"]
    resumen = df_dc.groupby("Fecha").agg({"Entradas": "sum", "Cancelados": "sum"}).reset_index()
    fig = px.bar(resumen, x="Fecha", y=["Entradas", "Cancelados"], barmode="group", title="📅 Doc. Consentimiento vs Cancelados por Día")
    st.plotly_chart(fig, use_container_width=True)
    mostrar_conclusion(f"📆 Día con más cancelados: **{resumen.loc[resumen['Cancelados'].idxmax(), 'Fecha']}**")

# Conclusiones generales
mostrar_conclusiones(df_view)
