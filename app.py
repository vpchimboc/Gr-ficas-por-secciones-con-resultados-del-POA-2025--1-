import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Dashboard POA 2025", layout="wide")

st.title("📊 Dashboard de Seguimiento POA 2025")
st.markdown("Visualización interactiva de avances por secciones y búsqueda por unidad.")

@st.cache_data
def load_data():
    file_path = 'RESUMEN.xlsx'
    xl = pd.ExcelFile(file_path)
    
    # 1. POA Institucional
    df_inst = pd.read_excel(xl, 'POA INSTITUCIONAL')
    def clean_pct(val):
        if isinstance(val, str):
            try:
                return float(val.replace('%', ''))
            except:
                return 0.0
        return float(val) * 100 if val <= 1 else float(val)
    df_inst['PORCENTAJE'] = df_inst['PORCENTAJE'].apply(clean_pct)
    
    # 2. Proyectos
    df_proy = pd.read_excel(xl, 'PROYECTOS')
    df_proy['% Ejecutado'] = df_proy['% Ejecutado'].apply(lambda x: x * 100 if x <= 1 else x)
    
    # 3. Unidades Administrativas
    df_admin = pd.read_excel(xl, 'UNIDADES ADMINISTRATIVAS')
    df_admin['PORCENTAJE DE AVANCE FINAL'] = df_admin['PORCENTAJE DE AVANCE FINAL'].apply(clean_pct)
    
    # 4. Unidades Académicas
    df_acad = pd.read_excel(xl, 'UNIDADES ACADÉMICAS')
    df_acad['PORCENTAJE DE AVANCE FINAL'] = df_acad['PORCENTAJE DE AVANCE FINAL'].apply(clean_pct)
    
    # 5. Carreras
    df_carr = pd.read_excel(xl, 'CARRERAS', skiprows=3)
    df_carr = df_carr.iloc[:, [0, 19]]
    df_carr.columns = ['CARRERA', 'AVANCE']
    df_carr = df_carr.dropna(subset=['CARRERA'])
    df_carr['AVANCE'] = df_carr['AVANCE'].apply(lambda x: x * 100 if pd.notnull(x) and x <= 1 else x)
    
    return df_inst, df_proy, df_admin, df_acad, df_carr

try:
    df_inst, df_proy, df_admin, df_acad, df_carr = load_data()

    # Sidebar para navegación
    st.sidebar.header("Navegación")
    menu = st.sidebar.selectbox("Seleccione Sección", ["Resumen General", "Búsqueda por Unidad", "Revisión Detallada"])

    if menu == "Resumen General":
        st.header("📈 Resumen por Secciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("POA Institucional")
            fig_inst = px.bar(df_inst, x='OBJETIVO OPERATIVO', y='PORCENTAJE', 
                             title="Avance por Objetivo Operativo",
                             labels={'PORCENTAJE': 'Avance (%)'},
                             color='PORCENTAJE', color_continuous_scale='Viridis',
                             text_auto='.2f')
            st.plotly_chart(fig_inst, use_container_width=True)
            
            st.subheader("Unidades Administrativas")
            fig_admin = px.bar(df_admin, x='UNIDADES', y='PORCENTAJE DE AVANCE FINAL',
                              title="Avance Unidades Administrativas",
                              labels={'PORCENTAJE DE AVANCE FINAL': 'Avance (%)'},
                              color='PORCENTAJE DE AVANCE FINAL', color_continuous_scale='Blues',
                              text_auto='.2f')
            st.plotly_chart(fig_admin, use_container_width=True)

        with col2:
            st.subheader("Proyectos")
            fig_proy = px.bar(df_proy, x='Nombre del proyecto', y='% Ejecutado',
                             title="Avance de Proyectos",
                             labels={'% Ejecutado': 'Ejecución (%)'},
                             color='% Ejecutado', color_continuous_scale='Reds',
                             text_auto='.2f')
            st.plotly_chart(fig_proy, use_container_width=True)
            
            st.subheader("Unidades Académicas")
            fig_acad = px.bar(df_acad, x='UNIDADES', y='PORCENTAJE DE AVANCE FINAL',
                             title="Avance Unidades Académicas",
                             labels={'PORCENTAJE DE AVANCE FINAL': 'Avance (%)'},
                             color='PORCENTAJE DE AVANCE FINAL', color_continuous_scale='Greens',
                             text_auto='.2f')
            st.plotly_chart(fig_acad, use_container_width=True)
            
        st.subheader("Carreras")
        fig_carr = px.bar(df_carr, x='CARRERA', y='AVANCE',
                         title="Avance por Carrera",
                         labels={'AVANCE': 'Avance (%)'},
                         color='AVANCE', color_continuous_scale='Magma',
                         text_auto='.2f')
        st.plotly_chart(fig_carr, use_container_width=True)

    elif menu == "Búsqueda por Unidad":
        st.header("🔍 Búsqueda de Desempeño por Unidad")
        
        # Consolidar todas las unidades para la búsqueda
        unidades_admin = df_admin[['UNIDADES', 'PORCENTAJE DE AVANCE FINAL']].rename(columns={'UNIDADES': 'Nombre', 'PORCENTAJE DE AVANCE FINAL': 'Avance'})
        unidades_acad = df_acad[['UNIDADES', 'PORCENTAJE DE AVANCE FINAL']].rename(columns={'UNIDADES': 'Nombre', 'PORCENTAJE DE AVANCE FINAL': 'Avance'})
        carreras = df_carr[['CARRERA', 'AVANCE']].rename(columns={'CARRERA': 'Nombre', 'AVANCE': 'Avance'})
        proyectos = df_proy[['Nombre del proyecto', '% Ejecutado']].rename(columns={'Nombre del proyecto': 'Nombre', '% Ejecutado': 'Avance'})
        
        all_units = pd.concat([unidades_admin, unidades_acad, carreras, proyectos], ignore_index=True)
        all_units = all_units.dropna(subset=['Nombre'])
        
        search_term = st.selectbox("Seleccione o busque la unidad/proyecto/carrera:", sorted(all_units['Nombre'].unique()))
        
        if search_term:
            res = all_units[all_units['Nombre'] == search_term].iloc[0]
            
            col_m1, col_m2 = st.columns([1, 2])
            with col_m1:
                st.metric(label=f"Avance de: {search_term}", value=f"{res['Avance']:.2f}%")
            
            with col_m2:
                # Gráfica de Gauge con Plotly Graph Objects
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = res['Avance'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Cumplimiento POA 2025", 'font': {'size': 24}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "darkblue"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(255, 0, 0, 0.3)'},
                            {'range': [50, 80], 'color': 'rgba(255, 255, 0, 0.3)'},
                            {'range': [80, 100], 'color': 'rgba(0, 255, 0, 0.3)'}],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90}}))
                
                fig_gauge.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "darkblue", 'family': "Arial"})
                st.plotly_chart(fig_gauge, use_container_width=True)

    elif menu == "Revisión Detallada":
        st.header("🔗 Enlaces de Revisión Detallada")
        st.markdown("A continuación se presentan los enlaces para revisar la información a detalle por cada sección:")
        
        # Crear una tabla de enlaces
        enlaces = {
            "Sección": ["POA Institucional", "Proyectos", "Unidades Administrativas", "Unidades Académicas", "Carreras"],
            "Descripción": [
                "Detalle de objetivos operativos institucionales.",
                "Seguimiento individual de proyectos de inversión y gestión.",
                "Cumplimiento de metas de las unidades administrativas.",
                "Avance de las facultades y coordinaciones académicas.",
                "Resultados de cumplimiento por cada carrera académica."
            ],
            "Acción": [
                "[Ver Detalle](https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=136683976#gid=136683976)", "[Ver Detalle](https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=250699039#gid=250699039)", "[Ver Detalle](https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=2078135518#gid=2078135518)", "[Ver Detalle](https://docs.google.com/spreadsheets/d/1-9bknOKLNSER3jkoLOYJz0MYzkx1peDl/edit?gid=380430315#gid=380430315)", "[Ver Detalle](https://docs.google.com/spreadsheets/d/1FYv0ZFXwqOkbo2YYTGuW2ommKCmk9jTU/edit?gid=1746760684#gid=1746760684)"
            ]
        }
        st.table(pd.DataFrame(enlaces))
        
        st.info("Nota: Los enlaces anteriores son marcadores de posición. Puede integrar URLs específicas de su sistema de gestión aquí.")

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.info("Asegúrese de que el archivo 'RESUMEN.xlsx' esté en la carpeta 'upload'.")
