import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_all_data, get_aggregated_inventory

# Configuración de la página
st.set_page_config(
    page_title="Panel de Control SunMarket",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏪 Panel de Control - SunMarket")
st.markdown("---")
st.markdown("**Su herramienta para tomar mejores decisiones comerciales**")

# Mensaje de bienvenida personalizado
st.info("""
👋 **¡Bienvenido/a!** Este panel le ayudará a:
- 📊 Conocer el estado actual de su inventario
- 💰 Monitorear las ventas diarias y tendencias
- 🎯 Identificar oportunidades de mejora
- ⚠️ Recibir alertas sobre productos que necesitan atención

**¿Cómo usar este panel?** Use el menú lateral para navegar entre las diferentes secciones.
""")

# Cargar datos para métricas principales
try:
    # Cargar datos temporales completos
    inventory_temporal, sales, transactions = load_all_data()
    
    # Obtener datos agregados de inventario
    inventory = get_aggregated_inventory()
    
    # Métricas principales con explicaciones claras
    st.subheader("📊 Resumen de Su Negocio")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        productos_unicos = inventory['codigo_producto'].nunique()
        st.metric(
            "Productos Únicos", 
            productos_unicos, 
            help="Número de productos diferentes que maneja en su tienda"
        )
    
    with col2:
        total_ventas = sales['ventas_totales_clp'].sum()
        st.metric(
            "Ventas Totales", 
            f"${total_ventas:,.0f}", 
            help="Total de dinero recaudado por ventas"
        )
    
    with col3:
        total_transacciones = transactions['numero_transacciones'].sum()
        st.metric(
            "Clientes Atendidos", 
            f"{total_transacciones:,}", 
            help="Número total de clientes que han comprado"
        )
    
    with col4:
        if total_transacciones > 0:
            ticket_promedio = total_ventas / total_transacciones
            st.metric(
                "Compra Promedio", 
                f"${ticket_promedio:,.0f}", 
                help="Cuánto gasta en promedio cada cliente"
            )
        else:
            st.metric("Compra Promedio", "$0")
    
    # Alertas importantes para el dueño
    st.subheader("🚨 Alertas Importantes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Productos que necesitan atención
        productos_criticos = inventory[inventory['alerta_stock'] == 'CRÍTICO']
        productos_bajo = inventory[inventory['alerta_stock'] == 'BAJO']
        
        if len(productos_criticos) > 0:
            st.error(f"🚨 **{len(productos_criticos)} productos necesitan reposición URGENTE**")
            st.write("Productos críticos:")
            for _, prod in productos_criticos.head(3).iterrows():
                st.write(f"• {prod['descripcion']} (promedio: {prod['stock_actual']:.0f} unidades)")
            if len(productos_criticos) > 3:
                st.write(f"... y {len(productos_criticos) - 3} más")
        
        if len(productos_bajo) > 0:
            st.warning(f"⚠️ **{len(productos_bajo)} productos están quedando pocos**")
            st.write("Considere reponer pronto:")
            for _, prod in productos_bajo.head(3).iterrows():
                st.write(f"• {prod['descripcion']} (promedio: {prod['stock_actual']:.0f} unidades)")
            if len(productos_bajo) > 3:
                st.write(f"... y {len(productos_bajo) - 3} más")
    
    with col2:
        # Productos con exceso
        productos_exceso = inventory[inventory['alerta_stock'] == 'EXCESO']
        
        if len(productos_exceso) > 0:
            st.info(f"📦 **{len(productos_exceso)} productos tienen demasiado stock**")
            st.write("Considere promociones para:")
            for _, prod in productos_exceso.head(3).iterrows():
                st.write(f"• {prod['descripcion']} (promedio: {prod['stock_actual']:.0f} unidades)")
            if len(productos_exceso) > 3:
                st.write(f"... y {len(productos_exceso) - 3} más")
        
        # Estado general del inventario
        productos_normales = inventory[inventory['alerta_stock'] == 'NORMAL']
        st.success(f"✅ **{len(productos_normales)} productos están en buen estado**")
    
    # Gráficos simples y claros
    st.subheader("📈 Tendencias de Su Negocio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estado del inventario con colores claros
        alert_counts = inventory['alerta_stock'].value_counts()
        
        # Traducir estados a lenguaje de negocio
        estados_negocio = {
            'NORMAL': 'Stock Adecuado',
            'BAJO': 'Necesita Reposición',
            'CRÍTICO': 'Reposición Urgente',
            'EXCESO': 'Demasiado Stock'
        }
        
        alert_counts_traducido = alert_counts.rename(index=estados_negocio)
        
        fig_inventory = px.pie(
            values=alert_counts_traducido.values,
            names=alert_counts_traducido.index,
            title="Estado Actual de Su Inventario",
            color_discrete_map={
                'Stock Adecuado': '#28a745',
                'Necesita Reposición': '#ffc107',
                'Reposición Urgente': '#dc3545',
                'Demasiado Stock': '#17a2b8'
            }
        )
        fig_inventory.update_traces(textposition='inside', textinfo='percent+label')
        fig_inventory.update_layout(showlegend=False)
        st.plotly_chart(fig_inventory, use_container_width=True)
    
    with col2:
        # Ventas de los últimos 30 días
        sales_recent = sales.tail(30)
        fig_sales = px.line(
            sales_recent,
            x='fecha',
            y='ventas_totales_clp',
            title="Ventas de los Últimos 30 Días",
            labels={'ventas_totales_clp': 'Ventas ($)', 'fecha': 'Fecha'}
        )
        fig_sales.update_traces(line_color='#007bff', line_width=3)
        fig_sales.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Ventas ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_sales, use_container_width=True)
    
except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.info("Asegúrate de que los archivos CSV estén en la carpeta 'data/'")

# Navegación simplificada para el dueño
st.markdown("---")
st.subheader("🧭 Explore Sus Datos")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("""
    **� Estado del Inventario**
    
    Vea el estado detallado de todos sus productos:
    - ¿Qué productos necesitan reposición?
    - ¿Cuáles se venden más rápido?
    - ¿Qué productos tienen demasiado stock?
    
    💡 **Perfecto para:** Planificar compras y reposiciones
    """)
    
with col2:
    st.info("""
    **� Análisis de Ventas**
    
    Analice cómo van sus ventas día a día:
    - ¿Cuánto vende cada día?
    - ¿Cuántos clientes atiende?
    - ¿Cuál es el ticket promedio?
    
    💡 **Perfecto para:** Entender las tendencias de su negocio
    """)
    
with col3:
    st.warning("""
    **🎯 Análisis de Productos**
    
    Descubra patrones en sus productos usando Machine Learning:
    - ¿Qué productos se comportan similar?
    - ¿Cómo optimizar el inventario?
    - ¿Qué estrategias aplicar?
    
    💡 **Perfecto para:** Estrategias de negocio avanzadas
    """)

# Consejos útiles para el dueño
st.markdown("---")
st.subheader("💡 Consejos para Su Negocio")

with st.expander("� Cómo interpretar las alertas de stock"):
    st.markdown("""
    - **🟢 Stock Adecuado**: Sus productos están bien, no necesita hacer nada
    - **🟡 Necesita Reposición**: Pronto se le van a acabar, planifique comprar más
    - **🔴 Reposición Urgente**: Se le está acabando YA, compre urgentemente
    - **🔵 Demasiado Stock**: Tiene mucho guardado, considere hacer promociones
    """)

with st.expander("📈 Cómo usar el análisis de ventas"):
    st.markdown("""
    - **Ventas altas**: Días donde vendió más, identifique qué funcionó bien
    - **Ventas bajas**: Días flojos, piense en promociones para esos días
    - **Tendencias**: Si las ventas suben o bajan constantemente
    - **Ticket promedio**: Si cada cliente compra más o menos que antes
    """)

with st.expander("🎯 Para qué sirve el análisis de Machine Learning"):
    st.markdown("""
    - **Productos similares**: Encuentre productos que se comportan igual usando clustering
    - **Estrategias por grupo**: Aplique las mismas estrategias a productos similares
    - **Optimización**: Mejore el manejo de inventario por grupos
    - **Decisiones basadas en datos**: Base sus decisiones en análisis, no solo en intuición
    """)

# Información adicional
st.markdown("---")
st.subheader("ℹ️ Acerca de Sus Datos")

with st.expander("📋 ¿De dónde vienen estos datos?"):
    st.markdown("""
    **Fuente:** Sistema de ventas e inventario de SunMarket
    
    **Incluye:**
    - Información de stock actual de todos sus productos
    - Historial de ventas diarias
    - Registro de transacciones (clientes atendidos)
    
    **Período analizado:** Datos actualizados de su negocio
    
    **Nota importante:** Estos datos son reales de su tienda y le ayudarán a tomar mejores decisiones.
    """)

with st.expander("⚠️ Limitaciones y Consideraciones Éticas"):
    st.markdown("""
    **📊 Limitaciones del Análisis:**
    - Los datos reflejan patrones históricos que pueden no repetirse en el futuro
    - Los algoritmos de agrupación son aproximaciones y deben validarse con experiencia comercial
    - Las predicciones son estimaciones basadas en tendencias pasadas
    - Los datos pueden contener errores de registro o medición
    
    **🔒 Consideraciones Éticas y Privacidad:**
    - Se preserva la confidencialidad de la información comercial
    - No se exponen datos personales de clientes individuales
    - Los análisis se basan en datos agregados y anonimizados
    - El uso de estos datos debe cumplir con regulaciones locales de protección de datos
    
    **⚖️ Recomendaciones de Uso Responsable:**
    - Use estos análisis como apoyo, no como única fuente de decisiones
    - Valide las recomendaciones con su experiencia comercial
    - Considere factores externos no capturados en los datos (temporadas, eventos, etc.)
    - Revise y actualice regularmente las interpretaciones basadas en nuevos datos
    
    **🎯 Transparencia del Modelo:**
    - Clustering K-means: Agrupa productos con características similares
    - PCA: Reduce dimensionalidad para visualización, puede perder información
    - Las métricas son calculadas en base a promedios históricos
    - Los umbrales de alertas son configurables y pueden ajustarse según necesidades
    """)

# Footer amigable
st.markdown("---")
st.markdown("*Panel de Control SunMarket - Datos actualizados para ayudarle a crecer su negocio*")
st.markdown("**¿Necesita ayuda?** Use el menú lateral para navegar entre las diferentes secciones.")
