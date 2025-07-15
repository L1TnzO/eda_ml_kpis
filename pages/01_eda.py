import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_inventory_data

# Configuración de la página
st.set_page_config(
    page_title="EDA - Inventario",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análisis Exploratorio de Datos - Inventario")
st.markdown("---")

# Cargar datos
try:
    datos = load_inventory_data()
    st.success(f"✅ Datos cargados exitosamente: {len(datos)} productos")
    
    # Mostrar primeras filas
    with st.expander("👁️ Vista previa de los datos"):
        st.dataframe(datos.head())
        
        # Información básica del dataset
        st.markdown("**Información del dataset:**")
        st.write(f"- Número de productos: {len(datos)}")
        st.write(f"- Columnas: {list(datos.columns)}")
        st.write(f"- Valores nulos: {datos.isnull().sum().sum()}")
    
    # Estadísticas descriptivas
    st.subheader("📈 Estadísticas Descriptivas")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Estadísticas numéricas:**")
        numeric_cols = ['stock_actual', 'dias_con_ventas', 'venta_promedio_diaria', 'dias_inventario_disponible']
        st.dataframe(datos[numeric_cols].describe())
    
    with col2:
        st.markdown("**Distribución de alertas de stock:**")
        alert_counts = datos['alerta_stock'].value_counts()
        
        # Crear gráfico de pie más detallado
        colors = {
            'CRÍTICO': '#ff4444',
            'BAJO': '#ffaa00', 
            'NORMAL': '#44ff44',
            'EXCESO': '#0088ff'
        }
        
        fig_pie = px.pie(
            values=alert_counts.values, 
            names=alert_counts.index,
            title="Distribución de Alertas de Stock",
            color=alert_counts.index,
            color_discrete_map=colors
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Visualizaciones principales
    st.subheader("📊 Visualizaciones Principales")
    
    # Fila 1: Histograma y Box plot
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(
            datos, 
            x='dias_inventario_disponible',
            title="Distribución de Días de Inventario Disponible",
            nbins=15,
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(
            xaxis_title="Días de Inventario",
            yaxis_title="Frecuencia"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        fig_box = px.box(
            datos, 
            x='alerta_stock', 
            y='dias_inventario_disponible',
            title="Días de Inventario por Nivel de Alerta",
            color='alerta_stock',
            color_discrete_map=colors
        )
        fig_box.update_layout(
            xaxis_title="Nivel de Alerta",
            yaxis_title="Días de Inventario"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Fila 2: Scatter plot y gráfico de barras
    col1, col2 = st.columns(2)
    
    with col1:
        fig_scatter = px.scatter(
            datos, 
            x='stock_actual', 
            y='venta_promedio_diaria',
            color='alerta_stock',
            size='dias_inventario_disponible',
            hover_data=['descripcion'],
            title="Relación: Stock Actual vs Venta Promedio Diaria",
            color_discrete_map=colors
        )
        fig_scatter.update_layout(
            xaxis_title="Stock Actual",
            yaxis_title="Venta Promedio Diaria"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Top 10 productos con más días de inventario
        top_inventory = datos.nlargest(10, 'dias_inventario_disponible')
        fig_bar = px.bar(
            top_inventory, 
            x='dias_inventario_disponible', 
            y='descripcion',
            title="Top 10 Productos con Más Días de Inventario",
            orientation='h',
            color='alerta_stock',
            color_discrete_map=colors
        )
        fig_bar.update_layout(
            xaxis_title="Días de Inventario",
            yaxis_title="Producto"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Análisis de correlación
    st.subheader("🔗 Análisis de Correlación")
    
    # Calcular matriz de correlación
    numeric_cols = ['stock_actual', 'dias_con_ventas', 'venta_promedio_diaria', 'dias_inventario_disponible']
    corr_matrix = datos[numeric_cols].corr()
    
    # Crear heatmap
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title="Matriz de Correlación",
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1
    )
    fig_corr.update_layout(
        width=600,
        height=500
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Análisis de productos críticos
    st.subheader("⚠️ Análisis de Productos Críticos")
    
    # Filtrar productos por categoría
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Productos en estado CRÍTICO:**")
        productos_criticos = datos[datos['alerta_stock'] == 'CRÍTICO']
        if not productos_criticos.empty:
            st.dataframe(productos_criticos[['descripcion', 'stock_actual', 'dias_inventario_disponible']])
        else:
            st.info("✅ No hay productos en estado crítico")
    
    with col2:
        st.markdown("**Productos con EXCESO de inventario:**")
        productos_exceso = datos[datos['alerta_stock'] == 'EXCESO']
        if not productos_exceso.empty:
            st.dataframe(productos_exceso[['descripcion', 'stock_actual', 'dias_inventario_disponible']])
        else:
            st.info("✅ No hay productos con exceso de inventario")
    
    # Análisis de rotación
    st.subheader("🔄 Análisis de Rotación de Productos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Productos de alta rotación (< 20 días):**")
        alta_rotacion = datos[datos['dias_inventario_disponible'] < 20]
        if not alta_rotacion.empty:
            st.dataframe(alta_rotacion[['descripcion', 'venta_promedio_diaria', 'dias_inventario_disponible']])
        else:
            st.info("No hay productos de alta rotación")
    
    with col2:
        st.markdown("**Productos de baja rotación (> 60 días):**")
        baja_rotacion = datos[datos['dias_inventario_disponible'] > 60]
        if not baja_rotacion.empty:
            st.dataframe(baja_rotacion[['descripcion', 'venta_promedio_diaria', 'dias_inventario_disponible']])
        else:
            st.info("No hay productos de baja rotación")
    
    # Insights y recomendaciones
    st.subheader("💡 Insights y Recomendaciones")
    
    # Calcular estadísticas clave
    promedio_dias = datos['dias_inventario_disponible'].mean()
    mediana_dias = datos['dias_inventario_disponible'].median()
    productos_normales = len(datos[datos['alerta_stock'] == 'NORMAL'])
    productos_atencion = len(datos[datos['alerta_stock'].isin(['CRÍTICO', 'BAJO'])])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **📊 Estadísticas Clave:**
        - Promedio de días de inventario: {promedio_dias:.1f} días
        - Mediana de días de inventario: {mediana_dias:.1f} días
        - Productos en estado normal: {productos_normales} ({productos_normales/len(datos)*100:.1f}%)
        - Productos que requieren atención: {productos_atencion} ({productos_atencion/len(datos)*100:.1f}%)
        """)
    
    with col2:
        st.warning("""
        **🎯 Recomendaciones:**
        - Monitorear productos con stock < 7 días
        - Evaluar descuentos para productos > 90 días
        - Optimizar reposición para productos de alta rotación
        - Revisar estrategia para productos con baja rotación
        """)
    
    # Consideraciones y limitaciones
    st.subheader("⚠️ Consideraciones y Limitaciones")
    st.warning("""
    **Limitaciones del análisis:**
    - Los datos son sintéticos y no reflejan patrones reales de consumo
    - La muestra es limitada (26 productos)
    - Los niveles de alerta son estimaciones basadas en promedios históricos
    - Se requiere validación con datos reales antes de tomar decisiones comerciales
    
    **Consideraciones éticas:**
    - Este análisis no debe ser el único criterio para decisiones de inventario
    - Se debe considerar factores externos como estacionalidad y tendencias de mercado
    - La interpretación de resultados debe ser realizada por personal especializado
    """)

except Exception as e:
    st.error(f"❌ Error al cargar o procesar los datos: {str(e)}")
    st.info("Asegúrate de que el archivo 'dias_inventario.csv' esté en la carpeta 'data/'")
    st.code("""
    Estructura esperada:
    sunmarket-dashboard/
    ├── data/
    │   └── dias_inventario.csv
    └── pages/
        └── 01_eda.py
    """)

# Footer
st.markdown("---")
st.markdown("*Análisis EDA - SunMarket Analytics Dashboard*")
