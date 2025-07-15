import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_sales_data, load_transactions_data

# Configuración de la página
st.set_page_config(
    page_title="KPIs Temporales",
    page_icon="📈",
    layout="wide"
)

st.title("📈 KPIs Temporales - SunMarket")
st.markdown("---")
st.markdown("**Análisis de indicadores clave de rendimiento en el tiempo**")

# Cargar datos
try:
    ventas = load_sales_data()
    transacciones = load_transactions_data()
    
    st.success(f"✅ Datos cargados: {len(ventas)} días de ventas, {len(transacciones)} días de transacciones")
    
    # Filtros en la sidebar
    st.sidebar.header("📅 Filtros de Fecha")
    
    # Obtener rango de fechas
    fecha_min = min(ventas['fecha'].min(), transacciones['fecha'].min())
    fecha_max = max(ventas['fecha'].max(), transacciones['fecha'].max())
    
    fecha_inicio = st.sidebar.date_input(
        "Fecha de inicio",
        value=fecha_min,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    fecha_fin = st.sidebar.date_input(
        "Fecha de fin",
        value=fecha_max,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    # Aplicar filtros
    ventas_filtradas = ventas[
        (ventas['fecha'] >= pd.to_datetime(fecha_inicio)) & 
        (ventas['fecha'] <= pd.to_datetime(fecha_fin))
    ]
    
    transacciones_filtradas = transacciones[
        (transacciones['fecha'] >= pd.to_datetime(fecha_inicio)) & 
        (transacciones['fecha'] <= pd.to_datetime(fecha_fin))
    ]
    
    # Validar que hay datos después del filtro
    if ventas_filtradas.empty or transacciones_filtradas.empty:
        st.error("❌ No hay datos para el rango de fechas seleccionado")
        st.stop()
    
    # Métricas principales del período
    st.subheader("📊 Métricas del Período Seleccionado")
    
    total_ventas = ventas_filtradas['ventas_totales_clp'].sum()
    total_transacciones = transacciones_filtradas['numero_transacciones'].sum()
    venta_promedio = total_ventas / total_transacciones if total_transacciones > 0 else 0
    dias_activos = len(ventas_filtradas)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Ventas Totales",
            f"{total_ventas:,.0f} CLP",
            help="Suma total de ventas en el período"
        )
    
    with col2:
        st.metric(
            "🛒 Total Transacciones",
            f"{total_transacciones:,}",
            help="Número total de transacciones"
        )
    
    with col3:
        st.metric(
            "💳 Venta Promedio",
            f"{venta_promedio:,.0f} CLP",
            help="Venta promedio por transacción"
        )
    
    with col4:
        st.metric(
            "📅 Días Activos",
            f"{dias_activos}",
            help="Días con datos en el período"
        )
    
    # KPI 1: Ventas Diarias
    st.subheader("💰 KPI 1: Evolución de Ventas Diarias")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_ventas = px.line(
            ventas_filtradas,
            x='fecha',
            y='ventas_totales_clp',
            title="Evolución de Ventas Diarias",
            labels={
                'fecha': 'Fecha',
                'ventas_totales_clp': 'Ventas (CLP)'
            }
        )
        fig_ventas.update_traces(line_color='#1f77b4', line_width=2)
        fig_ventas.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_ventas, use_container_width=True)
    
    with col2:
        st.markdown("**📊 Estadísticas de Ventas:**")
        st.metric("Promedio diario", f"{ventas_filtradas['ventas_totales_clp'].mean():,.0f} CLP")
        st.metric("Máximo", f"{ventas_filtradas['ventas_totales_clp'].max():,.0f} CLP")
        st.metric("Mínimo", f"{ventas_filtradas['ventas_totales_clp'].min():,.0f} CLP")
        st.metric("Desviación estándar", f"{ventas_filtradas['ventas_totales_clp'].std():,.0f} CLP")
    
    # KPI 2: Transacciones Diarias
    st.subheader("🛒 KPI 2: Número de Transacciones Diarias")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_transacciones = px.line(
            transacciones_filtradas,
            x='fecha',
            y='numero_transacciones',
            title="Número de Transacciones Diarias",
            labels={
                'fecha': 'Fecha',
                'numero_transacciones': 'Número de Transacciones'
            }
        )
        fig_transacciones.update_traces(line_color='#ff7f0e', line_width=2)
        fig_transacciones.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_transacciones, use_container_width=True)
    
    with col2:
        st.markdown("**📊 Estadísticas de Transacciones:**")
        st.metric("Promedio diario", f"{transacciones_filtradas['numero_transacciones'].mean():.1f}")
        st.metric("Máximo", f"{transacciones_filtradas['numero_transacciones'].max()}")
        st.metric("Mínimo", f"{transacciones_filtradas['numero_transacciones'].min()}")
        st.metric("Desviación estándar", f"{transacciones_filtradas['numero_transacciones'].std():.1f}")
    
    # KPI 3: Venta Promedio por Transacción
    st.subheader("💳 KPI 3: Venta Promedio por Transacción")
    
    # Combinar datos para calcular venta promedio
    merged_data = ventas_filtradas.merge(transacciones_filtradas, on='fecha', how='inner')
    merged_data['venta_por_transaccion'] = (
        merged_data['ventas_totales_clp'] / merged_data['numero_transacciones']
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_promedio = px.line(
            merged_data,
            x='fecha',
            y='venta_por_transaccion',
            title="Venta Promedio por Transacción",
            labels={
                'fecha': 'Fecha',
                'venta_por_transaccion': 'Venta por Transacción (CLP)'
            }
        )
        fig_promedio.update_traces(line_color='#2ca02c', line_width=2)
        fig_promedio.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_promedio, use_container_width=True)
    
    with col2:
        st.markdown("**📊 Estadísticas de Venta Promedio:**")
        st.metric("Promedio", f"{merged_data['venta_por_transaccion'].mean():,.0f} CLP")
        st.metric("Máximo", f"{merged_data['venta_por_transaccion'].max():,.0f} CLP")
        st.metric("Mínimo", f"{merged_data['venta_por_transaccion'].min():,.0f} CLP")
        st.metric("Desviación estándar", f"{merged_data['venta_por_transaccion'].std():,.0f} CLP")
    
    # Análisis Combinado
    st.subheader("📊 Análisis Combinado de KPIs")
    
    # Normalizar datos para comparación
    ventas_norm = (merged_data['ventas_totales_clp'] / merged_data['ventas_totales_clp'].max()) * 100
    transacciones_norm = (merged_data['numero_transacciones'] / merged_data['numero_transacciones'].max()) * 100
    venta_promedio_norm = (merged_data['venta_por_transaccion'] / merged_data['venta_por_transaccion'].max()) * 100
    
    fig_combined = go.Figure()
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=ventas_norm,
        mode='lines',
        name='Ventas (normalizado)',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=transacciones_norm,
        mode='lines',
        name='Transacciones (normalizado)',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=venta_promedio_norm,
        mode='lines',
        name='Venta Promedio (normalizado)',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig_combined.update_layout(
        title="Comparación Normalizada de KPIs (0-100%)",
        xaxis_title="Fecha",
        yaxis_title="Valor Normalizado (%)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)
    
    # Análisis de correlación entre KPIs
    st.subheader("🔗 Análisis de Correlación entre KPIs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Matriz de correlación
        correlation_data = merged_data[['ventas_totales_clp', 'numero_transacciones', 'venta_por_transaccion']]
        correlation_matrix = correlation_data.corr()
        
        fig_corr = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            title="Matriz de Correlación entre KPIs",
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with col2:
        # Scatter plot: Ventas vs Transacciones
        fig_scatter = px.scatter(
            merged_data,
            x='numero_transacciones',
            y='ventas_totales_clp',
            size='venta_por_transaccion',
            hover_data=['fecha'],
            title="Relación: Transacciones vs Ventas",
            labels={
                'numero_transacciones': 'Número de Transacciones',
                'ventas_totales_clp': 'Ventas Totales (CLP)'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Insights y conclusiones
    st.subheader("💡 Insights y Conclusiones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **📊 Resumen del Período:**
        - Período analizado: {fecha_inicio} a {fecha_fin}
        - Días con datos: {dias_activos}
        - Ventas totales: {total_ventas:,.0f} CLP
        - Transacciones totales: {total_transacciones:,}
        - Venta promedio por transacción: {venta_promedio:,.0f} CLP
        """)
    
    with col2:
        # Calcular correlación entre ventas y transacciones
        corr_ventas_trans = correlation_matrix.loc['ventas_totales_clp', 'numero_transacciones']
        
        st.success(f"""
        **🎯 Hallazgos Clave:**
        - Correlación ventas-transacciones: {corr_ventas_trans:.3f}
        - Variabilidad en ventas: {(ventas_filtradas['ventas_totales_clp'].std()/ventas_filtradas['ventas_totales_clp'].mean())*100:.1f}%
        - Día con mayores ventas: {ventas_filtradas.loc[ventas_filtradas['ventas_totales_clp'].idxmax(), 'fecha'].strftime('%Y-%m-%d')}
        - Día con más transacciones: {transacciones_filtradas.loc[transacciones_filtradas['numero_transacciones'].idxmax(), 'fecha'].strftime('%Y-%m-%d')}
        """)
    
    # Consideraciones y limitaciones
    st.subheader("⚠️ Consideraciones y Limitaciones")
    st.warning("""
    **Limitaciones del análisis temporal:**
    - Los datos son sintéticos y pueden no reflejar patrones estacionales reales
    - No se consideran factores externos como días festivos, promociones, o eventos especiales
    - Se requiere más contexto de negocio para interpretar correctamente las variaciones
    
    **Recomendaciones para el uso:**
    - Complementar con análisis de factores externos
    - Validar patrones con datos históricos reales
    - Considerar estacionalidad y ciclos de negocio
    - Usar como herramienta de monitoreo, no como única fuente de decisiones
    """)

except Exception as e:
    st.error(f"❌ Error al cargar o procesar los datos: {str(e)}")
    st.info("Asegúrate de que los archivos 'ventas_diarias.csv' y 'transacciones_diarias.csv' estén en la carpeta 'data/'")

# Footer
st.markdown("---")
st.markdown("*Análisis KPIs Temporales - SunMarket Analytics Dashboard*")
