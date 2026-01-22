import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Dashboard POA 2025",
    layout="wide"
)


col_logo1, col_titulo, col_logo2 = st.columns([1, 4, 1])

with col_logo1:
    st.image("LOGO1.jpg", width=120)

with col_titulo:
    st.markdown(
        "<h2 style='text-align: center;'>📊 Dashboard de Seguimiento POA 2025</h2>",
        unsafe_allow_html=True
    )

with col_logo2:
    st.image("LOGO2.png", width=120)
st.markdown("Visualización interactiva de avances, metas y desempeño institucional.")

# --------------------------------------------------
# TARGETS INSTITUCIONALES (%)
# --------------------------------------------------
TARGETS = {
    "POA Institucional": 90,
    "Proyectos": 85,
    "Unidades Administrativas": 88,
    "Unidades Académicas": 88,
    "Carreras": 85
}

# --------------------------------------------------
# CARGA Y LIMPIEZA DE DATOS
# --------------------------------------------------
@st.cache_data
def load_data():
    file_path = "RESUMEN.xlsx"
    xl = pd.ExcelFile(file_path)

    def clean_pct(val):
        if isinstance(val, str):
            try:
                return float(val.replace("%", ""))
            except:
                return 0.0
        if pd.isna(val):
            return 0.0
        return val * 100 if val <= 1 else val

    # POA Institucional
    df_inst = pd.read_excel(xl, "POA INSTITUCIONAL")
    df_inst["PORCENTAJE"] = df_inst["PORCENTAJE"].apply(clean_pct)

    # Proyectos
    df_proy = pd.read_excel(xl, "PROYECTOS")
    df_proy["% Ejecutado"] = df_proy["% Ejecutado"].apply(clean_pct)

    # Unidades Administrativas
    df_admin = pd.read_excel(xl, "UNIDADES ADMINISTRATIVAS")
    df_admin["PORCENTAJE DE AVANCE FINAL"] = df_admin["PORCENTAJE DE AVANCE FINAL"].apply(clean_pct)

    # Unidades Académicas
    df_acad = pd.read_excel(xl, "UNIDADES ACADÉMICAS")
    df_acad["PORCENTAJE DE AVANCE FINAL"] = df_acad["PORCENTAJE DE AVANCE FINAL"].apply(clean_pct)

    # Carreras
    df_carr = pd.read_excel(xl, "CARRERAS", skiprows=3)
    df_carr = df_carr.iloc[:, [0, 19]]
    df_carr.columns = ["CARRERA", "AVANCE"]
    df_carr = df_carr.dropna(subset=["CARRERA"])
    df_carr["AVANCE"] = df_carr["AVANCE"].apply(clean_pct)

    return df_inst, df_proy, df_admin, df_acad, df_carr


# --------------------------------------------------
# EJECUCIÓN PRINCIPAL
# --------------------------------------------------
try:
    df_inst, df_proy, df_admin, df_acad, df_carr = load_data()

    # --------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------
    st.sidebar.header("📂 Navegación")
    menu = st.sidebar.selectbox(
        "Seleccione la sección",
        ["Resumen General", "Búsqueda por Unidad", "Revisión Detallada"]
    )

    # ==================================================
    # RESUMEN GENERAL
    # ==================================================
    if menu == "Resumen General":

        st.header("📈 Resumen Ejecutivo y Cumplimiento de Metas")

        # PROMEDIOS
        prom_inst = df_inst["PORCENTAJE"].mean()
        prom_proy = df_proy["% Ejecutado"].mean()
        prom_admin = df_admin["PORCENTAJE DE AVANCE FINAL"].mean()
        prom_acad = df_acad["PORCENTAJE DE AVANCE FINAL"].mean()
        prom_carr = df_carr["AVANCE"].mean()

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("POA Institucional", f"{prom_inst:.2f}%", f"{prom_inst - TARGETS['POA Institucional']:.2f}%")
        c2.metric("Proyectos", f"{prom_proy:.2f}%", f"{prom_proy - TARGETS['Proyectos']:.2f}%")
        c3.metric("Unid. Administrativas", f"{prom_admin:.2f}%", f"{prom_admin - TARGETS['Unidades Administrativas']:.2f}%")
        c4.metric("Unid. Académicas", f"{prom_acad:.2f}%", f"{prom_acad - TARGETS['Unidades Académicas']:.2f}%")
        c5.metric("Carreras", f"{prom_carr:.2f}%", f"{prom_carr - TARGETS['Carreras']:.2f}%")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            fig_inst = px.bar(
                df_inst,
                x="OBJETIVO OPERATIVO",
                y="PORCENTAJE",
                title="Avance POA Institucional (%)",
                color="PORCENTAJE",
                text_auto=".2f"
            )
            st.plotly_chart(fig_inst, use_container_width=True)

            fig_admin = px.bar(
                df_admin,
                x="UNIDADES",
                y="PORCENTAJE DE AVANCE FINAL",
                title="Unidades Administrativas (%)",
                color="PORCENTAJE DE AVANCE FINAL",
                text_auto=".2f"
            )
            st.plotly_chart(fig_admin, use_container_width=True)

        with col2:
            fig_proy = px.bar(
                df_proy,
                x="Nombre del proyecto",
                y="% Ejecutado",
                title="Avance de Proyectos (%)",
                color="% Ejecutado",
                text_auto=".2f"
            )
            st.plotly_chart(fig_proy, use_container_width=True)

            fig_acad = px.bar(
                df_acad,
                x="UNIDADES",
                y="PORCENTAJE DE AVANCE FINAL",
                title="Unidades Académicas (%)",
                color="PORCENTAJE DE AVANCE FINAL",
                text_auto=".2f"
            )
            st.plotly_chart(fig_acad, use_container_width=True)

        fig_carr = px.bar(
            df_carr,
            x="CARRERA",
            y="AVANCE",
            title="Avance por Carrera (%)",
            color="AVANCE",
            text_auto=".2f"
        )
        st.plotly_chart(fig_carr, use_container_width=True)

    # ==================================================
    # BÚSQUEDA POR UNIDAD
    # ==================================================
    elif menu == "Búsqueda por Unidad":

        st.header("🔍 Consulta de Desempeño por Unidad / Proyecto / Carrera")

        unidades = pd.concat([
            df_admin[["UNIDADES", "PORCENTAJE DE AVANCE FINAL"]].rename(columns={"UNIDADES": "Nombre", "PORCENTAJE DE AVANCE FINAL": "Avance"}),
            df_acad[["UNIDADES", "PORCENTAJE DE AVANCE FINAL"]].rename(columns={"UNIDADES": "Nombre", "PORCENTAJE DE AVANCE FINAL": "Avance"}),
            df_carr[["CARRERA", "AVANCE"]].rename(columns={"CARRERA": "Nombre", "AVANCE": "Avance"}),
            df_proy[["Nombre del proyecto", "% Ejecutado"]].rename(columns={"Nombre del proyecto": "Nombre", "% Ejecutado": "Avance"})
        ], ignore_index=True)

        unidades = unidades.dropna(subset=["Nombre"])

        seleccion = st.selectbox(
            "Seleccione la unidad / proyecto / carrera",
            sorted(unidades["Nombre"].unique())
        )

        data = unidades[unidades["Nombre"] == seleccion].iloc[0]

        colm1, colm2 = st.columns([1, 2])
        colm1.metric(
            f"Avance de {seleccion}",
            f"{data['Avance']:.2f}%",
            f"{data['Avance'] - 85:.2f}% vs meta"
        )

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data["Avance"],
            gauge={
                "axis": {"range": [0, 100]},
                "steps": [
                    {"range": [0, 50], "color": "rgba(255,0,0,0.3)"},
                    {"range": [50, 80], "color": "rgba(255,255,0,0.3)"},
                    {"range": [80, 100], "color": "rgba(0,255,0,0.3)"}
                ],
                "threshold": {"value": 90}
            },
            title={"text": "Cumplimiento POA 2025"}
        ))

        colm2.plotly_chart(fig_gauge, use_container_width=True)

    # ==================================================
    # REVISIÓN DETALLADA
    # ==================================================
    elif menu == "Revisión Detallada":

        st.header("🔗 Acceso a Información Detallada")

        st.markdown("""
        <table style="width:100%; border-collapse: collapse;">
        <tr><th>Sección</th><th>Descripción</th><th>Acción</th></tr>

        <tr><td>POA Institucional</td><td>Objetivos operativos</td>
        <td><a href="https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=136683976#gid=136683976" target="_blank">Ver detalle</a></td></tr>

        <tr><td>Proyectos</td><td>Seguimiento de proyectos</td>
        <td><a href="https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=250699039#gid=250699039" target="_blank">Ver detalle</a></td></tr>

        <tr><td>Unidades Administrativas</td><td>Gestión administrativa</td>
        <td><a href="https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=2078135518#gid=2078135518" target="_blank">Ver detalle</a></td></tr>

        <tr><td>Unidades Académicas</td><td>Gestión académica</td>
        <td><a href="https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=380430315#gid=380430315" target="_blank">Ver detalle</a></td></tr>

        <tr><td>Carreras</td><td>Resultados por carrera</td>
        <td><a href="https://docs.google.com/spreadsheets/d/1FYv0ZFXwqOkbo2YYTGuW2ommKCmk9jTU/edit?gid=1746760684#gid=1746760684" target="_blank">Ver detalle</a></td></tr>
        </table>
        """, unsafe_allow_html=True)

    st.divider()
    st.image("LOGO_HORIZONTAL.png")
    
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
    st.info("Verifique que el archivo RESUMEN.xlsx esté en el directorio correcto.")
