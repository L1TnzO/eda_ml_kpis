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
    page_title="Análisis de Ventas",
    page_icon="📈",
    layout="wide"
)

st.title("📈 KPIs en el Tiempo")
st.markdown("---")
st.markdown("**Visualización de 3 indicadores clave a través del tiempo**")

# Cargar datos
try:
    ventas = load_sales_data()
    transacciones = load_transactions_data()
    
    st.success(f"✅ Datos cargados: {len(ventas)} días de ventas analizados")
    
    # Sidebar para filtros
    st.sidebar.header("🔧 Seleccione el Período a Analizar")
    
    # Filtros de fecha
    fecha_min = ventas['fecha'].min()
    fecha_max = ventas['fecha'].max()
    
    fecha_inicio = st.sidebar.date_input(
        "📅 Desde",
        value=fecha_min,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    fecha_fin = st.sidebar.date_input(
        "📅 Hasta",
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
    st.subheader("📊 Resumen de Su Negocio en el Período")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ventas = ventas_filtradas['ventas_totales_clp'].sum()
        st.metric(
            "💰 Total Vendido",
            f"${total_ventas:,.0f}",
            help="Dinero total que ingresó a su negocio"
        )
    
    with col2:
        total_transacciones = transacciones_filtradas['numero_transacciones'].sum()
        st.metric(
            "🛒 Clientes Atendidos",
            f"{total_transacciones:,}",
            help="Número total de clientes que compraron"
        )
    
    with col3:
        if total_transacciones > 0:
            venta_promedio = total_ventas / total_transacciones
            st.metric(
                "💳 Venta Promedio por Cliente",
                f"${venta_promedio:,.0f}",
                help="Cuánto gasta en promedio cada cliente"
            )
        else:
            st.metric("💳 Venta Promedio", "N/A")
    
    with col4:
        dias_analizados = len(ventas_filtradas)
        venta_diaria_promedio = total_ventas / dias_analizados if dias_analizados > 0 else 0
        st.metric(
            "📅 Venta Diaria Promedio",
            f"${venta_diaria_promedio:,.0f}",
            help="Cuánto vende en promedio por día"
        )
    
    # KPI 1: Ventas Diarias - Lenguaje de negocio
    st.subheader("💰 ¿Cómo Están Sus Ventas Día a Día?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_ventas = px.line(
            ventas_filtradas, 
            x='fecha', 
            y='ventas_totales_clp',
            title="Sus Ventas Diarias",
            labels={'ventas_totales_clp': 'Dinero Vendido ($)', 'fecha': 'Fecha'}
        )
        fig_ventas.update_traces(
            line=dict(color='#1f77b4', width=3),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.1)'
        )
        fig_ventas.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_ventas, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Información de Sus Ventas:**")
        promedio_ventas = ventas_filtradas['ventas_totales_clp'].mean()
        maximo_ventas = ventas_filtradas['ventas_totales_clp'].max()
        minimo_ventas = ventas_filtradas['ventas_totales_clp'].min()
        
        st.metric("Promedio Diario", f"${promedio_ventas:,.0f}")
        st.metric("Mejor Día", f"${maximo_ventas:,.0f}")
        st.metric("Día Más Bajo", f"${minimo_ventas:,.0f}")
        
        # Interpretación automática
        if maximo_ventas > promedio_ventas * 1.5:
            st.success("✅ Tiene días muy buenos!")
        if minimo_ventas < promedio_ventas * 0.5:
            st.warning("⚠️ Algunos días son más bajos")
    
    # KPI 2: Transacciones Diarias - Lenguaje de negocio
    st.subheader("🛒 ¿Cuántos Clientes Atiende por Día?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_trans = px.line(
            transacciones_filtradas, 
            x='fecha', 
            y='numero_transacciones',
            title="Clientes Atendidos por Día",
            labels={'numero_transacciones': 'Clientes Atendidos', 'fecha': 'Fecha'}
        )
        fig_trans.update_traces(
            line=dict(color='#ff7f0e', width=3),
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.1)'
        )
        fig_trans.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_trans, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Información de Sus Clientes:**")
        promedio_clientes = transacciones_filtradas['numero_transacciones'].mean()
        maximo_clientes = transacciones_filtradas['numero_transacciones'].max()
        minimo_clientes = transacciones_filtradas['numero_transacciones'].min()
        
        st.metric("Promedio Diario", f"{promedio_clientes:.0f} clientes")
        st.metric("Día Más Ocupado", f"{maximo_clientes} clientes")
        st.metric("Día Más Tranquilo", f"{minimo_clientes} clientes")
        
        # Interpretación automática
        if maximo_clientes > promedio_clientes * 1.5:
            st.info("💡 Tiene días muy ocupados - considere más personal")
        if minimo_clientes < promedio_clientes * 0.5:
            st.info("💡 Algunos días son más tranquilos - oportunidad de promociones")
    
    # KPI 3: Venta Promedio por Cliente - Lenguaje de negocio
    st.subheader("💳 ¿Cuánto Gasta Cada Cliente en Promedio?")
    
    # Fusionar datos para calcular venta promedio
    merged_data = ventas_filtradas.merge(transacciones_filtradas, on='fecha', how='inner')
    
    # Calcular venta promedio por transacción
    merged_data['venta_por_cliente'] = np.where(
        merged_data['numero_transacciones'] > 0,
        merged_data['ventas_totales_clp'] / merged_data['numero_transacciones'],
        0
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_promedio = px.line(
            merged_data, 
            x='fecha', 
            y='venta_por_cliente',
            title="Gasto Promedio por Cliente",
            labels={'venta_por_cliente': 'Gasto Promedio ($)', 'fecha': 'Fecha'}
        )
        fig_promedio.update_traces(
            line=dict(color='#2ca02c', width=3),
            fill='tonexty',
            fillcolor='rgba(44, 160, 44, 0.1)'
        )
        fig_promedio.update_layout(
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_promedio, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Información del Gasto:**")
        promedio_gasto = merged_data['venta_por_cliente'].mean()
        maximo_gasto = merged_data['venta_por_cliente'].max()
        minimo_gasto = merged_data['venta_por_cliente'].min()
        
        st.metric("Gasto Promedio", f"${promedio_gasto:,.0f}")
        st.metric("Mejor Día", f"${maximo_gasto:,.0f}")
        st.metric("Día Más Bajo", f"${minimo_gasto:,.0f}")
        
        # Interpretación automática
        if maximo_gasto > promedio_gasto * 1.5:
            st.success("✅ Algunos días sus clientes gastan mucho más!")
        if minimo_gasto < promedio_gasto * 0.5:
            st.info("💡 Algunos días el gasto es más bajo - oportunidad de promociones")
    
    # Análisis general para el dueño del negocio
    st.subheader("📊 Resumen General de Su Negocio")
    
    # Crear gráfico combinado simplificado
    fig_combined = go.Figure()
    
    # Escalar datos para visualización
    max_ventas = merged_data['ventas_totales_clp'].max()
    max_trans = merged_data['numero_transacciones'].max()
    max_gasto = merged_data['venta_por_cliente'].max()
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=merged_data['ventas_totales_clp'] / max_ventas * 100,
        mode='lines',
        name='Ventas Diarias',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=merged_data['numero_transacciones'] / max_trans * 100,
        mode='lines',
        name='Clientes Diarios',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    fig_combined.add_trace(go.Scatter(
        x=merged_data['fecha'],
        y=merged_data['venta_por_cliente'] / max_gasto * 100,
        mode='lines',
        name='Gasto por Cliente',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig_combined.update_layout(
        title="Cómo Se Comporta Su Negocio (Todas las Métricas en Escala 0-100)",
        xaxis_title="Fecha",
        yaxis_title="Nivel (%)",
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)
    
    # Insights automáticos para el dueño
    st.subheader("💡 Lo Que Estos Números Significan para Su Negocio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Hallazgos Importantes:**")
        
        # Análisis de tendencias
        if len(merged_data) > 5:
            # Tendencia de ventas
            ventas_inicio = merged_data['ventas_totales_clp'].head(5).mean()
            ventas_final = merged_data['ventas_totales_clp'].tail(5).mean()
            
            if ventas_final > ventas_inicio * 1.1:
                st.success("✅ Sus ventas están creciendo!")
            elif ventas_final < ventas_inicio * 0.9:
                st.warning("⚠️ Sus ventas han bajado últimamente")
            else:
                st.info("📊 Sus ventas se mantienen estables")
            
            # Análisis de clientes
            clientes_inicio = merged_data['numero_transacciones'].head(5).mean()
            clientes_final = merged_data['numero_transacciones'].tail(5).mean()
            
            if clientes_final > clientes_inicio * 1.1:
                st.success("✅ Está atendiendo más clientes!")
            elif clientes_final < clientes_inicio * 0.9:
                st.warning("⚠️ Está atendiendo menos clientes")
            else:
                st.info("📊 El número de clientes es estable")
        
        # Análisis de variabilidad
        cv_ventas = merged_data['ventas_totales_clp'].std() / merged_data['ventas_totales_clp'].mean()
        if cv_ventas > 0.3:
            st.info("📊 Sus ventas varían bastante entre días")
        else:
            st.success("✅ Sus ventas son consistentes")
    
    with col2:
        st.markdown("**🎯 Recomendaciones para Su Negocio:**")
        
        # Recomendaciones basadas en datos
        recomendaciones = []
        
        # Días de alta venta
        mejor_dia = merged_data.loc[merged_data['ventas_totales_clp'].idxmax()]
        dia_semana = mejor_dia['fecha'].strftime('%A')
        recomendaciones.append(f"📅 Su mejor día fue {dia_semana} - considere promociones especiales este día")
        
        # Gasto promedio
        if promedio_gasto < 5000:
            recomendaciones.append("💰 El gasto promedio es bajo - pruebe ofertas por volumen")
        elif promedio_gasto > 20000:
            recomendaciones.append("💰 Sus clientes gastan bien - mantenga la calidad")
        
        # Variabilidad de clientes
        if merged_data['numero_transacciones'].std() > merged_data['numero_transacciones'].mean() * 0.3:
            recomendaciones.append("👥 La cantidad de clientes varía mucho - considere promociones en días bajos")
        
        # Mostrar recomendaciones
        for i, rec in enumerate(recomendaciones, 1):
            st.markdown(f"{i}. {rec}")
        
        if not recomendaciones:
            st.success("✅ Su negocio está operando bien!")
    
    # Correlación simplificada
    st.subheader("🔗 Relación Entre Sus Métricas")
    
    correlacion_ventas_clientes = merged_data['ventas_totales_clp'].corr(merged_data['numero_transacciones'])
    correlacion_ventas_gasto = merged_data['ventas_totales_clp'].corr(merged_data['venta_por_cliente'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if correlacion_ventas_clientes > 0.7:
            st.success(f"✅ **Relación Fuerte:** Más clientes = más ventas ({correlacion_ventas_clientes:.2f})")
        elif correlacion_ventas_clientes > 0.3:
            st.info(f"📊 **Relación Moderada:** Más clientes generalmente = más ventas ({correlacion_ventas_clientes:.2f})")
        else:
            st.warning(f"⚠️ **Relación Débil:** Clientes y ventas no están muy relacionados ({correlacion_ventas_clientes:.2f})")
    
    with col2:
        if correlacion_ventas_gasto > 0.7:
            st.success(f"✅ **Relación Fuerte:** Cuando los clientes gastan más, las ventas suben ({correlacion_ventas_gasto:.2f})")
        elif correlacion_ventas_gasto > 0.3:
            st.info(f"📊 **Relación Moderada:** Gasto por cliente impacta las ventas ({correlacion_ventas_gasto:.2f})")
        else:
            st.warning(f"⚠️ **Relación Débil:** Gasto individual no afecta mucho las ventas totales ({correlacion_ventas_gasto:.2f})")

    # Limitaciones y consideraciones éticas específicas de KPIs
    st.markdown("---")
    st.subheader("⚠️ Limitaciones del Análisis de KPIs")
    
    with st.expander("📊 Consideraciones Importantes sobre los Indicadores"):
        st.markdown("""
        **Limitaciones Técnicas:**
        - Los KPIs reflejan tendencias pasadas que pueden no repetirse en el futuro
        - Los promedios pueden ocultar variabilidad significativa entre períodos
        - Las correlaciones no implican causalidad entre variables
        - Los datos pueden estar influenciados por factores externos no capturados
        
        **Consideraciones Éticas:**
        - Los análisis se basan en datos comerciales agregados sin información personal de clientes
        - Las tendencias mostradas son descriptivas, no predictivas
        - Los algoritmos pueden tener sesgos en la interpretación de patrones
        - Se preserva la confidencialidad de la información comercial sensible
        
        **Recomendaciones de Uso:**
        - Use estos KPIs como indicadores, no como certezas absolutas
        - Considere factores estacionales, eventos especiales y contexto económico
        - Valide las tendencias con conocimiento del negocio y experiencia práctica
        - Actualice regularmente los análisis con datos más recientes
        - Combine estos insights con otros indicadores cualitativos del negocio
        """)

except Exception as e:
    st.error(f"❌ Error al cargar o procesar los datos: {str(e)}")
    st.info("Asegúrate de que los archivos estén en la carpeta 'data/'")
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
st.markdown("*Análisis de Ventas - SunMarket Dashboard*")
