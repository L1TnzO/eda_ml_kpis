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
st.markdown("**Análisis de indicadores clave de rendimiento a lo largo del tiempo**")

# Cargar datos
try:
    ventas = load_sales_data()
    transacciones = load_transactions_data()
    
    st.success(f"✅ Datos cargados exitosamente: {len(ventas)} días de ventas, {len(transacciones)} días de transacciones")
    
    # Sidebar para filtros
    st.sidebar.header("🔧 Filtros de Análisis")
    
    # Filtros de fecha
    fecha_min = ventas['fecha'].min()
    fecha_max = ventas['fecha'].max()
    
    fecha_inicio = st.sidebar.date_input(
        "📅 Fecha de inicio",
        value=fecha_min,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    fecha_fin = st.sidebar.date_input(
        "📅 Fecha de fin",
        value=fecha_max,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    # Validar rango de fechas
    if fecha_inicio > fecha_fin:
        st.sidebar.error("❌ La fecha de inicio debe ser anterior a la fecha de fin")
        st.stop()
    
    # Aplicar filtros
    ventas_filtradas = ventas[
        (ventas['fecha'] >= pd.to_datetime(fecha_inicio)) & 
        (ventas['fecha'] <= pd.to_datetime(fecha_fin))
    ]
    
    transacciones_filtradas = transacciones[
        (transacciones['fecha'] >= pd.to_datetime(fecha_inicio)) & 
        (transacciones['fecha'] <= pd.to_datetime(fecha_fin))
    ]
    
    # Verificar que hay datos después del filtro
    if len(ventas_filtradas) == 0 or len(transacciones_filtradas) == 0:
        st.warning("⚠️ No hay datos disponibles para el rango de fechas seleccionado")
        st.stop()
    
    # Métricas principales del período
    st.subheader("📊 Métricas del Período Seleccionado")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ventas = ventas_filtradas['ventas_totales_clp'].sum()
        st.metric(
            "💰 Ventas Totales",
            f"{total_ventas:,.0f} CLP",
            help="Suma total de ventas en el período"
        )
    
    with col2:
        total_transacciones = transacciones_filtradas['numero_transacciones'].sum()
        st.metric(
            "🛒 Total Transacciones",
            f"{total_transacciones:,}",
            help="Número total de transacciones en el período"
        )
    
    with col3:
        if total_transacciones > 0:
            venta_promedio = total_ventas / total_transacciones
            st.metric(
                "💳 Venta Promedio",
                f"{venta_promedio:,.0f} CLP",
                help="Venta promedio por transacción"
            )
        else:
            st.metric("💳 Venta Promedio", "N/A")
    
    with col4:
        dias_analizados = len(ventas_filtradas)
        st.metric(
            "📅 Días Analizados",
            f"{dias_analizados}",
            help="Número de días en el período"
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
            labels={'ventas_totales_clp': 'Ventas (CLP)', 'fecha': 'Fecha'}
        )
        fig_ventas.update_traces(
            line=dict(color='#1f77b4', width=2),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.1)'
        )
        fig_ventas.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_ventas, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Estadísticas:**")
        st.write(f"Promedio: {ventas_filtradas['ventas_totales_clp'].mean():,.0f} CLP")
        st.write(f"Máximo: {ventas_filtradas['ventas_totales_clp'].max():,.0f} CLP")
        st.write(f"Mínimo: {ventas_filtradas['ventas_totales_clp'].min():,.0f} CLP")
        st.write(f"Desv. Estándar: {ventas_filtradas['ventas_totales_clp'].std():,.0f} CLP")
    
    # KPI 2: Transacciones Diarias
    st.subheader("🛒 KPI 2: Número de Transacciones Diarias")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_trans = px.line(
            transacciones_filtradas, 
            x='fecha', 
            y='numero_transacciones',
            title="Número de Transacciones Diarias",
            labels={'numero_transacciones': 'Número de Transacciones', 'fecha': 'Fecha'}
        )
        fig_trans.update_traces(
            line=dict(color='#ff7f0e', width=2),
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.1)'
        )
        fig_trans.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_trans, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Estadísticas:**")
        st.write(f"Promedio: {transacciones_filtradas['numero_transacciones'].mean():.1f}")
        st.write(f"Máximo: {transacciones_filtradas['numero_transacciones'].max()}")
        st.write(f"Mínimo: {transacciones_filtradas['numero_transacciones'].min()}")
        st.write(f"Desv. Estándar: {transacciones_filtradas['numero_transacciones'].std():.1f}")
    
    # KPI 3: Venta Promedio por Transacción
    st.subheader("💳 KPI 3: Venta Promedio por Transacción")
    
    # Fusionar datos para calcular venta promedio
    merged_data = ventas_filtradas.merge(transacciones_filtradas, on='fecha', how='inner')
    
    # Calcular venta promedio por transacción
    merged_data['venta_por_transaccion'] = np.where(
        merged_data['numero_transacciones'] > 0,
        merged_data['ventas_totales_clp'] / merged_data['numero_transacciones'],
        0
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_promedio = px.line(
            merged_data, 
            x='fecha', 
            y='venta_por_transaccion',
            title="Venta Promedio por Transacción",
            labels={'venta_por_transaccion': 'Venta Promedio (CLP)', 'fecha': 'Fecha'}
        )
        fig_promedio.update_traces(
            line=dict(color='#2ca02c', width=2),
            fill='tonexty',
            fillcolor='rgba(44, 160, 44, 0.1)'
        )
        fig_promedio.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_promedio, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Estadísticas:**")
        st.write(f"Promedio: {merged_data['venta_por_transaccion'].mean():,.0f} CLP")
        st.write(f"Máximo: {merged_data['venta_por_transaccion'].max():,.0f} CLP")
        st.write(f"Mínimo: {merged_data['venta_por_transaccion'].min():,.0f} CLP")
        st.write(f"Desv. Estándar: {merged_data['venta_por_transaccion'].std():,.0f} CLP")
    
    # Análisis combinado
    st.subheader("📊 Análisis Combinado de KPIs")
    
    # Normalizar datos para comparación
    ventas_norm = (merged_data['ventas_totales_clp'] / merged_data['ventas_totales_clp'].max()) * 100
    trans_norm = (merged_data['numero_transacciones'] / merged_data['numero_transacciones'].max()) * 100
    venta_prom_norm = (merged_data['venta_por_transaccion'] / merged_data['venta_por_transaccion'].max()) * 100
    
    fig_combined = go.Figure()
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=ventas_norm,
        mode='lines',
        name='Ventas Diarias',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=trans_norm,
        mode='lines',
        name='Transacciones Diarias',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=venta_prom_norm,
        mode='lines',
        name='Venta Promedio',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig_combined.update_layout(
        title="Comparación Normalizada de KPIs (Valores 0-100)",
        xaxis_title="Fecha",
        yaxis_title="Valor Normalizado (%)",
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)
    
    # Análisis de correlación entre KPIs
    st.subheader("🔗 Análisis de Correlación entre KPIs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Matriz de correlación
        kpi_data = merged_data[['ventas_totales_clp', 'numero_transacciones', 'venta_por_transaccion']]
        corr_matrix = kpi_data.corr()
        
        fig_corr = px.imshow(
            corr_matrix,
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
            color='venta_por_transaccion',
            title="Relación: Transacciones vs Ventas",
            labels={
                'numero_transacciones': 'Número de Transacciones',
                'ventas_totales_clp': 'Ventas Totales (CLP)'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Análisis de tendencias
    st.subheader("📈 Análisis de Tendencias")
    
    # Calcular tendencias usando media móvil
    ventana = min(7, len(merged_data))  # Ventana de 7 días o menos si hay pocos datos
    
    merged_data['ventas_ma'] = merged_data['ventas_totales_clp'].rolling(window=ventana).mean()
    merged_data['transacciones_ma'] = merged_data['numero_transacciones'].rolling(window=ventana).mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_trend_ventas = px.line(
            merged_data,
            x='fecha',
            y=['ventas_totales_clp', 'ventas_ma'],
            title=f"Tendencia de Ventas (Media Móvil {ventana} días)",
            labels={'value': 'Ventas (CLP)', 'fecha': 'Fecha'}
        )
        fig_trend_ventas.update_traces(
            line=dict(width=2)
        )
        st.plotly_chart(fig_trend_ventas, use_container_width=True)
    
    with col2:
        fig_trend_trans = px.line(
            merged_data,
            x='fecha',
            y=['numero_transacciones', 'transacciones_ma'],
            title=f"Tendencia de Transacciones (Media Móvil {ventana} días)",
            labels={'value': 'Transacciones', 'fecha': 'Fecha'}
        )
        fig_trend_trans.update_traces(
            line=dict(width=2)
        )
        st.plotly_chart(fig_trend_trans, use_container_width=True)
    
    # Insights y análisis
    st.subheader("💡 Insights y Análisis")
    
    # Calcular correlación entre ventas y transacciones
    correlacion_ventas_trans = merged_data['ventas_totales_clp'].corr(merged_data['numero_transacciones'])
    
    # Identificar días con mejor y peor rendimiento
    dia_mejor_ventas = merged_data.loc[merged_data['ventas_totales_clp'].idxmax()]
    dia_peor_ventas = merged_data.loc[merged_data['ventas_totales_clp'].idxmin()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **📊 Correlaciones clave:**
        - Ventas vs Transacciones: {correlacion_ventas_trans:.3f}
        - Período analizado: {dias_analizados} días
        - Variabilidad en ventas: {(ventas_filtradas['ventas_totales_clp'].std() / ventas_filtradas['ventas_totales_clp'].mean() * 100):.1f}%
        
        **💰 Mejor día de ventas:**
        - Fecha: {dia_mejor_ventas['fecha'].strftime('%Y-%m-%d')}
        - Ventas: {dia_mejor_ventas['ventas_totales_clp']:,.0f} CLP
        - Transacciones: {dia_mejor_ventas['numero_transacciones']}
        """)
    
    with col2:
        st.warning(f"""
        **🎯 Recomendaciones de gestión:**
        - Monitor días con ventas < {ventas_filtradas['ventas_totales_clp'].quantile(0.25):,.0f} CLP
        - Aprovechar patrones de días con alto rendimiento
        - Optimizar días con pocas transacciones
        
        **📉 Día con menores ventas:**
        - Fecha: {dia_peor_ventas['fecha'].strftime('%Y-%m-%d')}
        - Ventas: {dia_peor_ventas['ventas_totales_clp']:,.0f} CLP
        - Transacciones: {dia_peor_ventas['numero_transacciones']}
        """)
    
    # Consideraciones y limitaciones
    st.subheader("⚠️ Consideraciones y Limitaciones")
    st.warning("""
    **Limitaciones del análisis temporal:**
    - Los datos son sintéticos y no reflejan patrones estacionales reales
    - No considera factores externos como promociones, días festivos, o eventos especiales
    - Los patrones identificados requieren validación con datos reales
    - Las correlaciones pueden ser artificiales debido a la naturaleza sintética de los datos
    
    **Consideraciones para la toma de decisiones:**
    - Utilizar este análisis como punto de partida, no como única fuente de información
    - Complementar con análisis cualitativos del comportamiento del cliente
    - Validar tendencias identificadas con datos históricos reales
    - Considerar factores externos que puedan influir en las ventas
    """)

except Exception as e:
    st.error(f"❌ Error al cargar o procesar los datos: {str(e)}")
    st.info("Asegúrate de que los archivos 'ventas_diarias.csv' y 'transacciones_diarias.csv' estén en la carpeta 'data/'")
    st.code("""
    Estructura esperada:
    sunmarket-dashboard/
    ├── data/
    │   ├── ventas_diarias.csv
    │   └── transacciones_diarias.csv
    └── pages/
        └── 02_kpis.py
    """)

# Footer
st.markdown("---")
st.markdown("*Análisis KPIs Temporales - SunMarket Analytics Dashboard*")
