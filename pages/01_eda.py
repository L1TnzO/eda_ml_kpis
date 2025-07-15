import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_inventory_data, get_aggregated_inventory

# Configuración de la página
st.set_page_config(
    page_title="Estado del Inventario",
    page_icon="�",
    layout="wide"
)

st.title("� Estado de Su Inventario")
st.markdown("---")
st.markdown("**Aquí puede ver el estado actual de todos sus productos y tomar decisiones informadas**")

# Mensaje introductorio
st.info("""
💡 **¿Qué encontrará aquí?**
- El estado actual de cada producto en su tienda
- Alertas sobre productos que necesitan atención
- Análisis de qué productos se venden más rápido
- Recomendaciones para optimizar su inventario
""")

# Cargar datos
try:
    # Cargar datos temporales completos
    datos_temporales = load_inventory_data()
    
    # Obtener datos agregados por producto
    datos = get_aggregated_inventory()
    
    productos_unicos = datos['codigo_producto'].nunique()
    registros_temporales = len(datos_temporales)
    
    st.success(f"✅ Analizando {productos_unicos} productos únicos ({registros_temporales} registros históricos)")
    
    # Información adicional sobre los datos
    st.info(f"""
    📊 **Datos procesados:**
    - {productos_unicos} productos únicos en su inventario
    - {registros_temporales} registros temporales analizados
    - {registros_temporales // productos_unicos} períodos promedio por producto
    - Los valores mostrados son promedios históricos para mejor análisis
    
    **📋 Distribución actual de alertas:**
    - 🔴 Críticos: {len(datos[datos['alerta_stock'] == 'CRÍTICO'])} productos
    - 🟡 Bajos: {len(datos[datos['alerta_stock'] == 'BAJO'])} productos  
    - 🟢 Normales: {len(datos[datos['alerta_stock'] == 'NORMAL'])} productos
    - 🔵 Exceso: {len(datos[datos['alerta_stock'] == 'EXCESO'])} productos
    
    💡 **Tip:** Use la página de "Análisis de Productos" para ver cómo se agrupan productos similares
    """)
    
    # Resumen ejecutivo para el dueño
    st.subheader("� Resumen de Su Inventario")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        productos_criticos = len(datos[datos['alerta_stock'] == 'CRÍTICO'])
        st.metric(
            "🚨 Productos Críticos", 
            productos_criticos,
            help="Productos que se van a agotar pronto y necesitan reposición urgente"
        )
    
    with col2:
        productos_bajo = len(datos[datos['alerta_stock'] == 'BAJO'])
        st.metric(
            "⚠️ Necesitan Reposición", 
            productos_bajo,
            help="Productos que pronto necesitarán ser repuestos"
        )
    
    with col3:
        productos_normales = len(datos[datos['alerta_stock'] == 'NORMAL'])
        st.metric(
            "✅ En Buen Estado", 
            productos_normales,
            help="Productos con stock adecuado"
        )
    
    with col4:
        productos_exceso = len(datos[datos['alerta_stock'] == 'EXCESO'])
        st.metric(
            "📦 Demasiado Stock", 
            productos_exceso,
            help="Productos con exceso de inventario - considere promociones"
        )
    
    # Interpretación en lenguaje de negocio con análisis más detallado
    total_productos = len(datos)
    porcentaje_criticos = (productos_criticos / total_productos) * 100
    porcentaje_normales = (productos_normales / total_productos) * 100
    porcentaje_exceso = (productos_exceso / total_productos) * 100
    
    # Análisis más sofisticado
    if porcentaje_criticos > 15:
        st.error(f"🚨 **ATENCIÓN URGENTE:** {porcentaje_criticos:.1f}% de sus productos necesitan reposición inmediata")
    elif porcentaje_criticos > 5:
        st.warning(f"⚠️ **Monitorear:** {porcentaje_criticos:.1f}% de sus productos están en estado crítico")
    
    if porcentaje_normales > 60:
        st.success(f"✅ **¡Excelente gestión!** {porcentaje_normales:.1f}% de sus productos están en buen estado")
    elif porcentaje_normales < 30:
        st.warning("⚠️ **Revise su planificación:** Pocos productos tienen stock adecuado")
    
    if porcentaje_exceso > 25:
        st.info(f"📦 **Optimización:** {porcentaje_exceso:.1f}% de sus productos tienen exceso - considere promociones")
    
    # Mensaje integrador con ML
    st.markdown("**🔗 Conexión con Análisis Inteligente:** Vaya a la página 'Análisis de Productos' para ver cómo se agrupan productos con comportamientos similares")
    
    # Visualizaciones claras para el dueño
    st.subheader("📊 Análisis Visual de Su Inventario")
    
    # Colores consistentes para el negocio
    colors = {
        'CRÍTICO': '#dc3545',
        'BAJO': '#ffc107', 
        'NORMAL': '#28a745',
        'EXCESO': '#17a2b8'
    }
    
    # Nombres más entendibles
    estados_negocio = {
        'CRÍTICO': 'Reposición Urgente',
        'BAJO': 'Necesita Reposición',
        'NORMAL': 'Stock Adecuado',
        'EXCESO': 'Demasiado Stock'
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de alertas traducida
        alert_counts = datos['alerta_stock'].value_counts()
        alert_counts_traducido = alert_counts.rename(index=estados_negocio)
        
        colors_traducidos = {
            'Reposición Urgente': '#dc3545',
            'Necesita Reposición': '#ffc107',
            'Stock Adecuado': '#28a745',
            'Demasiado Stock': '#17a2b8'
        }
        
        fig_pie = px.pie(
            values=alert_counts_traducido.values, 
            names=alert_counts_traducido.index,
            title="Estado General de Su Inventario",
            color_discrete_map=colors_traducidos
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Interpretación automática
        estado_dominante = alert_counts_traducido.index[0]
        porcentaje_dominante = (alert_counts_traducido.iloc[0] / len(datos)) * 100
        
        st.markdown(f"**💡 Interpretación:** {porcentaje_dominante:.1f}% de sus productos están en estado: **{estado_dominante}**")
    
    with col2:
        # Análisis de rotación en términos de negocio
        st.markdown("**🔄 Velocidad de Venta de Sus Productos**")
        
        # Categorizar productos por velocidad de venta con umbrales más precisos
        datos['velocidad_venta'] = pd.cut(
            datos['dias_inventario_disponible'], 
            bins=[0, 30, 50, 65, float('inf')],
            labels=['Muy Rápida', 'Rápida', 'Normal', 'Lenta']
        )
        
        velocidad_counts = datos['velocidad_venta'].value_counts()
        
        colors_velocidad = {
            'Muy Rápida': '#28a745',
            'Rápida': '#ffc107',
            'Normal': '#17a2b8',
            'Lenta': '#dc3545'
        }
        
        fig_velocidad = px.bar(
            x=velocidad_counts.index,
            y=velocidad_counts.values,
            title="Velocidad de Venta de Sus Productos",
            labels={'x': 'Velocidad de Venta', 'y': 'Cantidad de Productos'},
            color=velocidad_counts.index,
            color_discrete_map=colors_velocidad
        )
        fig_velocidad.update_layout(showlegend=False)
        st.plotly_chart(fig_velocidad, use_container_width=True)
        
        # Análisis más detallado de velocidad
        productos_muy_rapidos = len(datos[datos['velocidad_venta'] == 'Muy Rápida'])
        productos_rapidos = len(datos[datos['velocidad_venta'] == 'Rápida'])
        productos_lentos = len(datos[datos['velocidad_venta'] == 'Lenta'])
        
        if productos_muy_rapidos > 0:
            st.success(f"✅ Tiene {productos_muy_rapidos} productos de venta muy rápida - ¡priorice su disponibilidad!")
        
        if productos_rapidos > 0:
            st.info(f"📈 Tiene {productos_rapidos} productos de venta rápida - mantenga stock adecuado")
        
        if productos_lentos > 0:
            st.warning(f"⚠️ Tiene {productos_lentos} productos de venta lenta - considere estrategias de salida")
        
        # Conexión con análisis ML
        st.markdown("**🤖 Análisis Inteligente:** Estos productos de velocidad similar pueden agruparse en el análisis ML")
    
    # Tabla de productos que requieren atención inmediata
    st.subheader("⚠️ Productos Que Necesitan Su Atención Inmediata")
    
    # Productos críticos y con stock bajo
    productos_atencion = datos[datos['alerta_stock'].isin(['CRÍTICO', 'BAJO'])].copy()
    
    if len(productos_atencion) > 0:
        # Ordenar por prioridad (crítico primero, luego por días de inventario)
        productos_atencion['prioridad'] = productos_atencion['alerta_stock'].map({
            'CRÍTICO': 1,
            'BAJO': 2,
            'NORMAL': 3,
            'EXCESO': 4
        })
        productos_atencion = productos_atencion.sort_values(['prioridad', 'dias_inventario_disponible'])
        
        # Mostrar tabla simplificada
        tabla_simple = productos_atencion[[
            'descripcion', 'stock_actual', 'venta_promedio_diaria', 
            'dias_inventario_disponible', 'alerta_stock'
        ]].copy()
        
        # Renombrar columnas para el negocio
        tabla_simple.columns = [
            'Producto', 'Stock Actual', 'Venta Diaria Promedio', 
            'Días que Durará', 'Estado'
        ]
        
        # Traducir estados
        tabla_simple['Estado'] = tabla_simple['Estado'].map({
            'CRÍTICO': '🔴 Reposición Urgente',
            'BAJO': '🟡 Necesita Reposición',
            'NORMAL': '🟢 Stock Adecuado',
            'EXCESO': '🔵 Demasiado Stock'
        })
        
        st.dataframe(tabla_simple, use_container_width=True)
        
        # Resumen ejecutivo
        criticos = len(productos_atencion[productos_atencion['alerta_stock'] == 'CRÍTICO'])
        bajos = len(productos_atencion[productos_atencion['alerta_stock'] == 'BAJO'])
        
        st.markdown(f"**📋 Resumen de Acciones:**")
        if criticos > 0:
            st.error(f"🔴 {criticos} productos necesitan reposición URGENTE (se agotan pronto)")
        if bajos > 0:
            st.warning(f"🟡 {bajos} productos necesitan reposición en los próximos días")
        
        # Calcular valor total en riesgo
        valor_riesgo = productos_atencion['stock_actual'].sum()
        st.info(f"💰 Valor total de productos en riesgo: ${valor_riesgo:,.0f}")
    else:
        st.success("✅ ¡Excelente! No hay productos que requieran atención inmediata")
    
    # Productos con más oportunidad de venta
    st.subheader("� Sus Productos Estrella")
    
    # Productos con venta rápida y stock adecuado
    productos_estrella = datos[
        (datos['venta_promedio_diaria'] > datos['venta_promedio_diaria'].quantile(0.75)) &
        (datos['alerta_stock'] == 'NORMAL')
    ].copy()
    
    if len(productos_estrella) > 0:
        productos_estrella = productos_estrella.sort_values('venta_promedio_diaria', ascending=False)
        
        tabla_estrella = productos_estrella[[
            'descripcion', 'venta_promedio_diaria', 'stock_actual', 'dias_inventario_disponible'
        ]].head(10).copy()
        
        tabla_estrella.columns = [
            'Producto', 'Venta Diaria Promedio', 'Stock Actual', 'Días que Durará'
        ]
        
        st.dataframe(tabla_estrella, use_container_width=True)
        st.success(f"✅ Estos {len(tabla_estrella)} productos tienen alta demanda y stock adecuado - ¡manténgalos así!")
    else:
        st.info("No hay productos estrella identificados en este momento")
    
    # Recomendaciones automáticas
    st.subheader("💡 Recomendaciones para Su Negocio")
    
    recomendaciones = []
    
    # Análisis de stock crítico
    if len(datos[datos['alerta_stock'] == 'CRÍTICO']) > 0:
        recomendaciones.append("🔴 **Acción Inmediata:** Reponer productos críticos antes de que se agoten")
    
    # Análisis de exceso de stock
    exceso_stock = datos[datos['alerta_stock'] == 'EXCESO']
    if len(exceso_stock) > 0:
        recomendaciones.append(f"💙 **Oportunidad:** Tiene {len(exceso_stock)} productos con exceso de stock - considere promociones")
    
    # Análisis de diversificación
    productos_rapidos = len(datos[datos['dias_inventario_disponible'] < 15])
    if productos_rapidos > len(datos) * 0.1:
        recomendaciones.append("🚀 **Fortaleza:** Tiene muchos productos de rotación rápida - su mix es saludable")
    
    # Análisis de capital inmovilizado
    stock_total = datos['stock_actual'].sum()
    if stock_total > 0:
        recomendaciones.append(f"💰 **Capital en Inventario:** ${stock_total:,.0f} - optimice para liberar capital")
    
    for i, rec in enumerate(recomendaciones, 1):
        st.markdown(f"{i}. {rec}")
    
    if not recomendaciones:
        st.success("✅ Su inventario está bien balanceado - ¡siga así!")

    # Análisis de correlaciones entre variables
    st.subheader("📊 Relaciones Entre Variables de Su Inventario")
    
    # Preparar datos para análisis de correlación
    datos_numericos = datos[['stock_actual', 'venta_promedio_diaria', 'dias_inventario_disponible', 'dias_con_ventas']].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de dispersión: Stock vs Venta Diaria
        fig_scatter = px.scatter(
            datos, 
            x='stock_actual', 
            y='venta_promedio_diaria',
            color='alerta_stock',
            hover_data=['descripcion', 'dias_inventario_disponible'],
            title="Relación: Stock Actual vs Venta Diaria",
            labels={'stock_actual': 'Stock Actual', 'venta_promedio_diaria': 'Venta Diaria Promedio'},
            color_discrete_map={
                'CRÍTICO': '#dc3545',
                'BAJO': '#ffc107',
                'NORMAL': '#28a745',
                'EXCESO': '#17a2b8'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Interpretación del gráfico
        correlacion = datos['stock_actual'].corr(datos['venta_promedio_diaria'])
        if correlacion > 0.3:
            st.success(f"✅ **Correlación positiva moderada** (r={correlacion:.2f}): A mayor stock, mayor venta")
        elif correlacion < -0.3:
            st.warning(f"⚠️ **Correlación negativa** (r={correlacion:.2f}): Revise la gestión de stock")
        else:
            st.info(f"📊 **Correlación débil** (r={correlacion:.2f}): Stock y ventas no están fuertemente relacionados")
    
    with col2:
        # Gráfico de dispersión: Días de inventario vs Venta Diaria
        fig_scatter2 = px.scatter(
            datos, 
            x='dias_inventario_disponible', 
            y='venta_promedio_diaria',
            color='alerta_stock',
            hover_data=['descripcion', 'stock_actual'],
            title="Relación: Días de Inventario vs Venta Diaria",
            labels={'dias_inventario_disponible': 'Días de Inventario', 'venta_promedio_diaria': 'Venta Diaria Promedio'},
            color_discrete_map={
                'CRÍTICO': '#dc3545',
                'BAJO': '#ffc107',
                'NORMAL': '#28a745',
                'EXCESO': '#17a2b8'
            }
        )
        st.plotly_chart(fig_scatter2, use_container_width=True)
        
        # Interpretación del segundo gráfico
        correlacion2 = datos['dias_inventario_disponible'].corr(datos['venta_promedio_diaria'])
        if correlacion2 < -0.3:
            st.success(f"✅ **Relación esperada** (r={correlacion2:.2f}): Productos que se venden más duran menos")
        elif correlacion2 > 0.3:
            st.warning(f"⚠️ **Relación inesperada** (r={correlacion2:.2f}): Revise la planificación")
        else:
            st.info(f"📊 **Relación débil** (r={correlacion2:.2f}): Variabilidad normal en el negocio")
    
    # Análisis estadístico resumido
    st.markdown("**📈 Insights Estadísticos:**")
    
    # Encontrar productos con comportamiento atípico
    q75_stock = datos['stock_actual'].quantile(0.75)
    q25_venta = datos['venta_promedio_diaria'].quantile(0.25)
    
    productos_mucho_stock_poca_venta = datos[
        (datos['stock_actual'] > q75_stock) & 
        (datos['venta_promedio_diaria'] < q25_venta)
    ]
    
    if len(productos_mucho_stock_poca_venta) > 0:
        st.warning(f"⚠️ **{len(productos_mucho_stock_poca_venta)} productos** tienen mucho stock pero pocas ventas - considere promociones")
    
    # Productos con ventas altas pero poco stock
    q75_venta = datos['venta_promedio_diaria'].quantile(0.75)
    q25_stock = datos['stock_actual'].quantile(0.25)
    
    productos_poca_stock_alta_venta = datos[
        (datos['stock_actual'] < q25_stock) & 
        (datos['venta_promedio_diaria'] > q75_venta)
    ]
    
    if len(productos_poca_stock_alta_venta) > 0:
        st.success(f"✅ **{len(productos_poca_stock_alta_venta)} productos** tienen alta demanda - considere aumentar stock")
    
    st.markdown("**🔗 Conexión con ML:** Estas correlaciones ayudan al algoritmo a identificar productos con comportamientos similares")

    # Recomendaciones específicas basadas en los datos actuales
    st.subheader("💡 Recomendaciones Específicas para Su Negocio")
    
    recomendaciones = []
    
    # Análisis de productos críticos
    if len(datos[datos['alerta_stock'] == 'CRÍTICO']) > 0:
        productos_criticos_nombres = datos[datos['alerta_stock'] == 'CRÍTICO']['descripcion'].tolist()
        recomendaciones.append(f"🚨 **URGENTE:** Reponer inmediatamente: {', '.join(productos_criticos_nombres[:3])}")
        if len(productos_criticos_nombres) > 3:
            recomendaciones.append(f"   ... y {len(productos_criticos_nombres) - 3} productos más")
    
    # Análisis de productos con exceso
    if len(datos[datos['alerta_stock'] == 'EXCESO']) > 0:
        productos_exceso_nombres = datos[datos['alerta_stock'] == 'EXCESO']['descripcion'].tolist()
        recomendaciones.append(f"📦 **Promociones:** Considere ofertas para: {', '.join(productos_exceso_nombres[:3])}")
        if len(productos_exceso_nombres) > 3:
            recomendaciones.append(f"   ... y {len(productos_exceso_nombres) - 3} productos más")
    
    # Análisis de productos estrella
    productos_alta_rotacion = datos[datos['velocidad_venta'] == 'Muy Rápida']
    if len(productos_alta_rotacion) > 0:
        productos_estrella_nombres = productos_alta_rotacion['descripcion'].tolist()
        recomendaciones.append(f"⭐ **Productos estrella:** Mantenga siempre disponibles: {', '.join(productos_estrella_nombres[:3])}")
    
    # Análisis de rentabilidad potencial
    productos_oportunidad = datos[
        (datos['venta_promedio_diaria'] > datos['venta_promedio_diaria'].median()) &
        (datos['alerta_stock'] == 'NORMAL')
    ]
    if len(productos_oportunidad) > 0:
        recomendaciones.append(f"📈 **Oportunidad:** {len(productos_oportunidad)} productos tienen potencial de crecimiento")
    
    # Análisis de diversificación
    productos_lentos = datos[datos['velocidad_venta'] == 'Lenta']
    if len(productos_lentos) > 3:
        recomendaciones.append(f"🔄 **Diversificación:** Evaluar reemplazar {len(productos_lentos)} productos de rotación lenta")
    
    # Mostrar recomendaciones
    for i, rec in enumerate(recomendaciones, 1):
        st.markdown(f"{i}. {rec}")
    
    if not recomendaciones:
        st.success("✅ Su inventario está bien equilibrado. ¡Mantenga la buena gestión!")
    
    # Resumen ejecutivo final
    st.subheader("📋 Resumen Ejecutivo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎯 Acciones Inmediatas:**")
        if len(datos[datos['alerta_stock'] == 'CRÍTICO']) > 0:
            st.markdown("• Reposición urgente de productos críticos")
        else:
            st.markdown("• ✅ No hay acciones críticas")
        
        if len(datos[datos['alerta_stock'] == 'BAJO']) > 0:
            st.markdown("• Planificar reposición de productos bajos")
        else:
            st.markdown("• ✅ Stock bajo controlado")
    
    with col2:
        st.markdown("**📊 Optimizaciones:**")
        if len(datos[datos['alerta_stock'] == 'EXCESO']) > 0:
            st.markdown("• Crear promociones para productos con exceso")
        else:
            st.markdown("• ✅ No hay exceso de inventario")
        
        if len(productos_lentos) > 0:
            st.markdown("• Evaluar productos de rotación lenta")
        else:
            st.markdown("• ✅ Rotación de productos adecuada")
    
    with col3:
        st.markdown("**🚀 Oportunidades:**")
        if len(productos_alta_rotacion) > 0:
            st.markdown("• Potenciar productos de alta rotación")
        else:
            st.markdown("• Identificar productos estrella")
        
        st.markdown("• Usar análisis ML para insights avanzados")
    
    # Llamada a la acción
    st.info("🔗 **Próximo paso:** Vaya a la página 'Análisis de Productos' para ver cómo la inteligencia artificial puede ayudarle a optimizar su inventario")

    # ...existing code...

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
st.markdown("*Análisis de Inventario - SunMarket Dashboard*")
