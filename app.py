import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_all_data

# Configuración de la página
st.set_page_config(
    page_title="SunMarket Analytics Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏪 SunMarket Analytics Dashboard")
st.markdown("---")
st.markdown("**Dashboard de análisis para SunMarket - Datos de la capa Gold**")

# Cargar datos para métricas principales
try:
    inventory, sales, transactions = load_all_data()
    
    # Métricas principales
    st.subheader("📊 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_productos = len(inventory)
        st.metric("Total Productos", total_productos, delta=None, help="Productos en inventario")
    
    with col2:
        total_ventas = sales['ventas_totales_clp'].sum()
        st.metric("Ventas Totales", f"{total_ventas:,.0f} CLP", delta=None, help="Ventas acumuladas")
    
    with col3:
        total_transacciones = transactions['numero_transacciones'].sum()
        st.metric("Total Transacciones", f"{total_transacciones:,}", delta=None, help="Transacciones realizadas")
    
    with col4:
        dias_analizados = len(transactions)
        st.metric("Días Analizados", dias_analizados, delta=None, help="Días con datos")
    
    # Resumen rápido
    st.subheader("📈 Resumen Ejecutivo")
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de alertas de stock
        alert_counts = inventory['alerta_stock'].value_counts()
        fig_alerts = px.pie(
            values=alert_counts.values, 
            names=alert_counts.index,
            title="Estado del Inventario",
            color_discrete_map={
                'CRÍTICO': '#ff4444',
                'BAJO': '#ffaa00',
                'NORMAL': '#44ff44',
                'EXCESO': '#0088ff'
            }
        )
        st.plotly_chart(fig_alerts, use_container_width=True)
    
    with col2:
        # Tendencia de ventas (últimos 30 días)
        sales_recent = sales.tail(30)
        fig_trend = px.line(
            sales_recent, 
            x='fecha', 
            y='ventas_totales_clp',
            title="Tendencia de Ventas (Últimos 30 días)"
        )
        fig_trend.update_traces(line_color='#1f77b4')
        st.plotly_chart(fig_trend, use_container_width=True)
    
except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.info("Asegúrate de que los archivos CSV estén en la carpeta 'data/'")

# Navegación
st.markdown("---")
st.subheader("🧭 Navegación del Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **📊 EDA - Inventario**
    
    Análisis exploratorio detallado de los datos de inventario:
    - Estadísticas descriptivas
    - Distribuciones y outliers
    - Correlaciones entre variables
    - Análisis de niveles de alerta
    """)
    
with col2:
    st.success("""
    **📈 KPIs Temporales**
    
    Visualización de indicadores clave en el tiempo:
    - Evolución de ventas diarias
    - Número de transacciones
    - Venta promedio por transacción
    - Análisis de tendencias
    """)
    
with col3:
    st.warning("""
    **🤖 ML Analysis**
    
    Análisis avanzado con Machine Learning:
    - Clustering de productos
    - Proyección PCA
    - Segmentación automática
    - Recomendaciones basadas en datos
    """)

# Información adicional
st.markdown("---")
st.subheader("ℹ️ Información del Dataset")

with st.expander("📋 Detalles técnicos"):
    st.markdown("""
    **Fuente de datos:** Capa Gold - SunMarket Data Lake
    
    **Datasets utilizados:**
    - `dias_inventario.csv`: Análisis de rotación de productos
    - `transacciones_diarias.csv`: Actividad diaria de transacciones
    - `ventas_diarias.csv`: Ingresos diarios por ventas
    
    **Período de análisis:** 2023 completo (365 días)
    
    **Consideraciones:**
    - Datos generados artificialmente para fines académicos
    - Análisis debe validarse con datos reales en producción
    - Recomendaciones sujetas a verificación adicional
    """)

# Footer
st.markdown("---")
st.markdown("*Dashboard creado con Streamlit para SunMarket Analytics*")
st.markdown("**Instrucciones:** Usa el menú lateral para navegar entre las diferentes secciones del análisis.")
