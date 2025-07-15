import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_all_data, get_aggregated_inventory

# Configuración de la página
st.set_page_config(
    page_title="SunMarket Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏪 SunMarket Dashboard")
st.markdown("---")

# Información de navegación
st.info("""
📍 **Navegación:** Use el menú lateral para acceder a:
- 📊 **EDA Simplificado**: Análisis exploratorio de datos
- 📈 **KPIs**: Indicadores clave de rendimiento
- 🤖 **ML Simplificado**: Análisis de clustering
""")

# Cargar datos
try:
    # Cargar datos temporales completos
    inventory_temporal, sales, transactions = load_all_data()
    
    # Obtener datos agregados de inventario
    inventory = get_aggregated_inventory()
    
    # Métricas principales
    st.subheader("📊 Resumen General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        productos_unicos = inventory['codigo_producto'].nunique()
        st.metric("Productos Únicos", productos_unicos)
    
    with col2:
        total_ventas = sales['ventas_totales_clp'].sum()
        st.metric("Ventas Totales", f"${total_ventas:,.0f}")
    
    with col3:
        total_transacciones = transactions['numero_transacciones'].sum()
        st.metric("Transacciones", f"{total_transacciones:,}")
    
    with col4:
        if total_transacciones > 0:
            ticket_promedio = total_ventas / total_transacciones
            st.metric("Ticket Promedio", f"${ticket_promedio:,.0f}")
        else:
            st.metric("Ticket Promedio", "$0")
    
    # Distribución de alertas
    st.subheader("🚨 Estado del Inventario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de alertas
        alert_counts = inventory['alerta_stock'].value_counts()
        
        colors = {
            'CRÍTICO': '#dc3545',
            'BAJO': '#ffc107',
            'NORMAL': '#28a745',
            'EXCESO': '#17a2b8'
        }
        
        fig_pie = px.pie(
            values=alert_counts.values,
            names=alert_counts.index,
            title="Distribución de Alertas de Stock",
            color=alert_counts.index,
            color_discrete_map=colors
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Ventas recientes
        sales_recent = sales.tail(30)
        fig_sales = px.line(
            sales_recent,
            x='fecha',
            y='ventas_totales_clp',
            title="Ventas Últimos 30 Días"
        )
        st.plotly_chart(fig_sales, use_container_width=True)
    
    # Tabla de productos críticos
    st.subheader("⚠️ Productos Críticos")
    
    productos_criticos = inventory[inventory['alerta_stock'] == 'CRÍTICO']
    
    if len(productos_criticos) > 0:
        st.dataframe(
            productos_criticos[['descripcion', 'stock_actual', 'venta_promedio_diaria', 'dias_inventario_disponible']],
            use_container_width=True
        )
    else:
        st.success("✅ No hay productos críticos")

except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")

# Información de las páginas
st.markdown("---")
st.subheader("📋 Páginas Disponibles")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **📊 EDA Simplificado**
    
    Análisis exploratorio básico:
    - Estadísticas descriptivas
    - Distribuciones
    - Correlaciones
    """)

with col2:
    st.info("""
    **📈 KPIs**
    
    Indicadores clave:
    - Ventas diarias
    - Transacciones
    - Ticket promedio
    """)

with col3:
    st.info("""
    **🤖 ML Simplificado**
    
    Clustering K-Means:
    - Agrupación de productos
    - Visualizaciones
    - Interpretación
    """)

st.markdown("---")
st.markdown("*SunMarket Dashboard - Versión Simplificada*")
