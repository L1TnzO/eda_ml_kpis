import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_inventory_data, get_aggregated_inventory

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Productos",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Análisis Inteligente de Sus Productos")
st.markdown("---")
st.markdown("**Descubra qué productos se comportan de manera similar y cómo optimizar su negocio**")

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
    - Los valores mostrados son promedios históricos para mejor análisis
    """)
    
    productos_unicos = datos['codigo_producto'].nunique()
    registros_temporales = len(datos_temporales)
    
    st.success(f"✅ Analizando {productos_unicos} productos únicos ({registros_temporales} registros históricos)")
    
    # Información sobre procesamiento de datos con análisis de alertas
    st.info(f"""
    📊 **Datos procesados para análisis:**
    - {productos_unicos} productos únicos
    - {registros_temporales} registros temporales agregados
    - Métricas promedio calculadas para análisis más robusto
    
    **📋 Distribución de alertas de stock:**
    - 🔴 Críticos: {len(datos[datos['alerta_stock'] == 'CRÍTICO'])} productos
    - 🟡 Bajos: {len(datos[datos['alerta_stock'] == 'BAJO'])} productos  
    - 🟢 Normales: {len(datos[datos['alerta_stock'] == 'NORMAL'])} productos
    - 🔵 Exceso: {len(datos[datos['alerta_stock'] == 'EXCESO'])} productos
    """)
    
    # Sidebar simplificado
    st.sidebar.header("🔧 Configuración")
    
    # Explicación simple
    st.sidebar.info("""
    **¿Qué hace este análisis?**
    
    Usa inteligencia artificial para:
    - Agrupar productos similares
    - Identificar patrones de comportamiento
    - Ayudarle a tomar mejores decisiones
    """)
    
    # Configuración simplificada
    n_clusters = st.sidebar.slider(
        "¿En cuántos grupos dividir sus productos?",
        min_value=2,
        max_value=6,
        value=3,
        help="Más grupos = análisis más detallado"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Tip:** Comience con 3 grupos y ajuste según necesite")
    
    # Preparar datos para análisis
    st.subheader("🔍 Preparando el Análisis de Sus Productos")
    
    # Características principales para el análisis
    características = ['stock_actual', 'venta_promedio_diaria', 'dias_inventario_disponible']
    
    # Crear variable numérica para alerta de stock
    datos['alerta_numerica'] = datos['alerta_stock'].map({
        'CRÍTICO': 1,
        'BAJO': 2, 
        'NORMAL': 3,
        'EXCESO': 4
    })
    
    características_completas = características + ['alerta_numerica']
    
    # Verificar que las características existan
    características_disponibles = [col for col in características_completas if col in datos.columns]
    
    if len(características_disponibles) < 2:
        st.error("❌ No hay suficientes datos para el análisis")
        st.stop()
    
    # Información sobre qué se está analizando
    st.info(f"""
    **📊 Analizando sus productos basándose en:**
    - 📦 Stock actual que tiene
    - 📈 Cuánto vende por día en promedio
    - ⏰ Cuántos días le dura el inventario
    - 🚨 Estado de alerta de stock (Crítico/Bajo/Normal/Exceso)
    
    **🎯 Objetivo:** Encontrar productos con comportamientos similares para optimizar su gestión
    """)
    
    # Preparar datos para clustering
    datos_para_analisis = datos[características_disponibles].copy()
    
    # Manejar valores faltantes
    datos_para_analisis = datos_para_analisis.fillna(0)
    
    # Normalizar datos
    scaler = StandardScaler()
    datos_normalizados = scaler.fit_transform(datos_para_analisis)
    
    # Aplicar K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(datos_normalizados)
    
    # Agregar clusters a los datos originales
    datos_con_clusters = datos.copy()
    datos_con_clusters['Grupo'] = clusters
    
    # Crear nombres más entendibles para los grupos
    cluster_names = {
        0: "🔵 Grupo A",
        1: "🟢 Grupo B", 
        2: "🟡 Grupo C",
        3: "🔴 Grupo D",
        4: "🟣 Grupo E",
        5: "🟠 Grupo F"
    }
    
    datos_con_clusters['Grupo_Nombre'] = datos_con_clusters['Grupo'].map(cluster_names)
    
    # Calcular métricas de calidad del análisis
    silhouette_avg = silhouette_score(datos_normalizados, clusters)
    
    # Mostrar resultados del análisis
    st.subheader("📊 Resultados del Análisis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🎯 Calidad del Análisis",
            f"{silhouette_avg:.2f}",
            help="Entre 0 y 1. Mayor = mejor separación de grupos"
        )
    
    with col2:
        st.metric(
            "📦 Productos Analizados",
            f"{len(datos_con_clusters)}"
        )
    
    with col3:
        st.metric(
            "🔢 Grupos Creados",
            f"{n_clusters}"
        )
    
    # Interpretación de la calidad
    if silhouette_avg > 0.7:
        st.success("✅ ¡Excelente! Los grupos están muy bien definidos")
    elif silhouette_avg > 0.5:
        st.info("📊 Buena separación de grupos")
    elif silhouette_avg > 0.3:
        st.warning("⚠️ Separación moderada - considere ajustar el número de grupos")
    else:
        st.error("❌ Separación débil - intente con diferente número de grupos")
    
    # Visualización principal - Distribución de productos por grupo
    st.subheader("🎯 Sus Productos Divididos en Grupos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de distribución
        grupo_counts = datos_con_clusters['Grupo_Nombre'].value_counts()
        
        fig_dist = px.pie(
            values=grupo_counts.values,
            names=grupo_counts.index,
            title="Distribución de Productos por Grupo",
            color_discrete_map={
                "🔵 Grupo A": "#3498db",
                "🟢 Grupo B": "#2ecc71", 
                "🟡 Grupo C": "#f1c40f",
                "🔴 Grupo D": "#e74c3c",
                "🟣 Grupo E": "#9b59b6",
                "🟠 Grupo F": "#e67e22"
            }
        )
        fig_dist.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        st.markdown("**📋 Resumen por Grupo:**")
        for grupo, count in grupo_counts.items():
            porcentaje = (count / len(datos_con_clusters)) * 100
            st.markdown(f"**{grupo}:** {count} productos ({porcentaje:.1f}%)")
    
    # Análisis detallado de cada grupo
    st.subheader("🔍 ¿Qué Caracteriza a Cada Grupo?")
    
    for i in range(n_clusters):
        grupo_nombre = cluster_names[i]
        productos_grupo = datos_con_clusters[datos_con_clusters['Grupo'] == i]
        
        if len(productos_grupo) > 0:
            st.markdown(f"### {grupo_nombre}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Características promedio del grupo
                stock_promedio = productos_grupo['stock_actual'].mean()
                venta_promedio = productos_grupo['venta_promedio_diaria'].mean()
                dias_promedio = productos_grupo['dias_inventario_disponible'].mean()
                
                # Análisis de alertas en el grupo
                alertas_grupo = productos_grupo['alerta_stock'].value_counts()
                alerta_dominante = alertas_grupo.index[0] if len(alertas_grupo) > 0 else 'NORMAL'
                
                st.markdown(f"""
                **📊 Características típicas de este grupo:**
                - 📦 Stock promedio: {stock_promedio:.0f} unidades
                - 📈 Venta diaria promedio: {venta_promedio:.1f} unidades
                - ⏰ Días de inventario: {dias_promedio:.0f} días
                - 🚨 Alerta predominante: **{alerta_dominante}**
                """)
                
                # Interpretación automática mejorada
                if venta_promedio > datos['venta_promedio_diaria'].quantile(0.7):
                    st.success("✅ **Productos de alta rotación** - se venden rápido")
                elif venta_promedio < datos['venta_promedio_diaria'].quantile(0.3):
                    st.warning("⚠️ **Productos de baja rotación** - se venden lento")
                else:
                    st.info("📊 **Productos de rotación normal**")
                
                # Análisis específico por tipo de alerta
                if alerta_dominante == 'CRÍTICO':
                    st.error("🚨 **Grupo de ALTA PRIORIDAD** - Necesitan reposición urgente")
                elif alerta_dominante == 'BAJO':
                    st.warning("⚠️ **Grupo de ATENCIÓN** - Planifique reposición pronto")
                elif alerta_dominante == 'EXCESO':
                    st.info("📦 **Grupo de EXCESO** - Considere promociones o reducir pedidos")
                else:
                    st.success("✅ **Grupo ESTABLE** - Stock en niveles adecuados")
                
                if dias_promedio < 30:
                    st.info("⚡ **Necesitan reposición frecuente**")
                elif dias_promedio > 90:
                    st.warning("🐌 **Mucho tiempo en inventario**")
                
            with col2:
                # Lista de productos del grupo con sus alertas
                st.markdown(f"**🏷️ Productos en {grupo_nombre}:**")
                productos_mostrar = productos_grupo[['descripcion', 'alerta_stock']].head(5)
                for _, row in productos_mostrar.iterrows():
                    emoji_alerta = {'CRÍTICO': '🔴', 'BAJO': '🟡', 'NORMAL': '🟢', 'EXCESO': '🔵'}
                    emoji = emoji_alerta.get(row['alerta_stock'], '🟢')
                    st.markdown(f"- {emoji} {row['descripcion']}")
                
                if len(productos_grupo) > 5:
                    st.markdown(f"... y {len(productos_grupo) - 5} más")
                
                # Distribución de alertas en el grupo
                st.markdown("**📊 Distribución de alertas:**")
                for alerta, count in alertas_grupo.items():
                    emoji = emoji_alerta.get(alerta, '🟢')
                    porcentaje = (count / len(productos_grupo)) * 100
                    st.markdown(f"{emoji} {alerta}: {count} ({porcentaje:.0f}%)")
    
    # Visualización avanzada - Gráfico de dispersión
    st.subheader("📈 Visualización Avanzada de Sus Productos")
    
    # Usar PCA para reducir dimensionalidad si hay más de 2 características
    if len(características_disponibles) > 2:
        pca = PCA(n_components=2)
        datos_pca = pca.fit_transform(datos_normalizados)
        
        # Crear DataFrame para visualización
        df_viz = pd.DataFrame({
            'Componente 1': datos_pca[:, 0],
            'Componente 2': datos_pca[:, 1],
            'Grupo': datos_con_clusters['Grupo_Nombre'],
            'Producto': datos_con_clusters['descripcion'],
            'Stock': datos_con_clusters['stock_actual'],
            'Venta Diaria': datos_con_clusters['venta_promedio_diaria']
        })
        
        fig_scatter = px.scatter(
            df_viz,
            x='Componente 1',
            y='Componente 2',
            color='Grupo',
            hover_data=['Producto', 'Stock', 'Venta Diaria'],
            title="Mapa de Sus Productos (Vista Simplificada)",
            color_discrete_map={
                "🔵 Grupo A": "#3498db",
                "🟢 Grupo B": "#2ecc71", 
                "🟡 Grupo C": "#f1c40f",
                "🔴 Grupo D": "#e74c3c",
                "🟣 Grupo E": "#9b59b6",
                "🟠 Grupo F": "#e67e22"
            }
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.info("""
        **💡 Cómo leer este gráfico:**
        - Cada punto es un producto
        - Productos similares aparecen cerca
        - Colores diferentes = grupos diferentes
        - Pase el mouse sobre los puntos para ver detalles
        """)
    
    # Análisis de stock por grupo
    st.subheader("📦 Análisis de Stock por Grupo")
    
    # Calcular estadísticas por grupo
    stats_por_grupo = datos_con_clusters.groupby('Grupo_Nombre').agg({
        'stock_actual': ['mean', 'sum'],
        'venta_promedio_diaria': 'mean',
        'dias_inventario_disponible': 'mean'
    }).round(1)
    
    # Aplanar columnas
    stats_por_grupo.columns = ['Stock_Promedio', 'Stock_Total', 'Venta_Diaria_Promedio', 'Dias_Inventario_Promedio']
    
    # Crear gráfico de barras para stock total
    fig_stock = px.bar(
        x=stats_por_grupo.index,
        y=stats_por_grupo['Stock_Total'],
        title="Stock Total por Grupo",
        labels={'x': 'Grupo', 'y': 'Stock Total'},
        color=stats_por_grupo.index,
        color_discrete_map={
            "🔵 Grupo A": "#3498db",
            "🟢 Grupo B": "#2ecc71", 
            "🟡 Grupo C": "#f1c40f",
            "🔴 Grupo D": "#e74c3c",
            "🟣 Grupo E": "#9b59b6",
            "🟠 Grupo F": "#e67e22"
        }
    )
    fig_stock.update_layout(showlegend=False)
    st.plotly_chart(fig_stock, use_container_width=True)
    
    # Recomendaciones por grupo
    st.subheader("💡 Recomendaciones por Grupo")
    
    recomendaciones = []
    
    for i in range(n_clusters):
        grupo_nombre = cluster_names[i]
        productos_grupo = datos_con_clusters[datos_con_clusters['Grupo'] == i]
        
        if len(productos_grupo) > 0:
            stock_promedio = productos_grupo['stock_actual'].mean()
            venta_promedio = productos_grupo['venta_promedio_diaria'].mean()
            dias_promedio = productos_grupo['dias_inventario_disponible'].mean()
            
            # Análisis de alertas en el grupo
            alertas_grupo = productos_grupo['alerta_stock'].value_counts()
            alerta_dominante = alertas_grupo.index[0] if len(alertas_grupo) > 0 else 'NORMAL'
            
            # Generar recomendaciones específicas basadas en alertas
            if alerta_dominante == 'CRÍTICO':
                recomendaciones.append(f"**{grupo_nombre}:** 🚨 URGENTE - Reposición inmediata requerida")
            elif alerta_dominante == 'BAJO':
                recomendaciones.append(f"**{grupo_nombre}:** ⚠️ Planifique reposición en los próximos días")
            elif alerta_dominante == 'EXCESO':
                recomendaciones.append(f"**{grupo_nombre}:** 📦 Considere promociones para reducir stock")
            
            # Recomendaciones adicionales basadas en comportamiento
            if venta_promedio > datos['venta_promedio_diaria'].quantile(0.7):
                recomendaciones.append(f"**{grupo_nombre}:** 🚀 Productos estrella - priorice su disponibilidad")
            
            if dias_promedio < 15:
                recomendaciones.append(f"**{grupo_nombre}:** ⚡ Rotación muy rápida - considere sistema de reposición automática")
            
            if dias_promedio > 90:
                recomendaciones.append(f"**{grupo_nombre}:** 🐌 Rotación lenta - evalúe estrategias de salida")
            
            if stock_promedio > datos['stock_actual'].quantile(0.8):
                recomendaciones.append(f"**{grupo_nombre}:** � Alto stock - optimice niveles de inventario")
    
    # Mostrar recomendaciones
    for i, rec in enumerate(recomendaciones, 1):
        st.markdown(f"{i}. {rec}")
    
    if not recomendaciones:
        st.success("✅ Sus productos están bien balanceados en todos los grupos")
    
    # Tabla resumen final
    st.subheader("📋 Resumen Ejecutivo por Grupo")
    
    # Preparar tabla resumen
    tabla_resumen = stats_por_grupo.copy()
    tabla_resumen['Cantidad_Productos'] = datos_con_clusters.groupby('Grupo_Nombre').size()
    
    # Renombrar columnas para mejor comprensión
    tabla_resumen.columns = [
        'Stock Promedio', 'Stock Total', 'Venta Diaria Promedio', 
        'Días de Inventario Promedio', 'Cantidad de Productos'
    ]
    
    st.dataframe(tabla_resumen, use_container_width=True)
    
    # Insights finales
    st.subheader("🎯 Insights Clave para Su Negocio")
    
    insights = []
    
    # Identificar grupo con más productos
    grupo_mas_productos = datos_con_clusters['Grupo_Nombre'].value_counts().index[0]
    insights.append(f"📊 **Grupo predominante:** {grupo_mas_productos} representa la mayoría de sus productos")
    
    # Identificar grupo con mayor stock total
    grupo_mayor_stock = stats_por_grupo.loc[stats_por_grupo['Stock_Total'].idxmax()].name
    insights.append(f"📦 **Mayor inversión en stock:** {grupo_mayor_stock} concentra la mayor parte de su inventario")
    
    # Identificar grupo con mejor rotación
    grupo_mejor_rotacion = stats_por_grupo.loc[stats_por_grupo['Venta_Diaria_Promedio'].idxmax()].name
    insights.append(f"🚀 **Mejor rotación:** {grupo_mejor_rotacion} tiene los productos que más se venden")
    
    # Mostrar insights
    for insight in insights:
        st.markdown(f"- {insight}")
    
    # Explicación del análisis
    st.subheader("❓ ¿Cómo Funciona Este Análisis?")
    
    st.markdown("""
    **🤖 Inteligencia Artificial Aplicada a Su Negocio:**
    
    1. **Recolección de Datos:** Tomamos información de stock, ventas y tiempo de inventario
    2. **Normalización:** Ponemos todos los datos en la misma escala para comparar
    3. **Agrupación Inteligente:** El algoritmo K-means encuentra patrones similares
    4. **Validación:** Medimos qué tan bien separados están los grupos
    5. **Interpretación:** Traducimos los resultados a recomendaciones de negocio
    
    **💡 Beneficios para Su Negocio:**
    - Identificar productos similares para estrategias conjuntas
    - Optimizar niveles de inventario por categoría
    - Detectar oportunidades de mejora en productos específicos
    - Planificar compras y promociones de manera más efectiva
    """)

    # Análisis específico de productos críticos
    st.subheader("🚨 Análisis de Productos Críticos")
    
    productos_criticos = datos_con_clusters[datos_con_clusters['alerta_stock'] == 'CRÍTICO']
    productos_bajos = datos_con_clusters[datos_con_clusters['alerta_stock'] == 'BAJO']
    productos_exceso = datos_con_clusters[datos_con_clusters['alerta_stock'] == 'EXCESO']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔴 Productos Críticos**")
        if len(productos_criticos) > 0:
            st.error(f"**{len(productos_criticos)} productos necesitan atención URGENTE**")
            for _, prod in productos_criticos.iterrows():
                grupo_prod = prod['Grupo_Nombre']
                st.markdown(f"• {prod['descripcion']} ({grupo_prod})")
        else:
            st.success("✅ No hay productos críticos")
    
    with col2:
        st.markdown("**🟡 Productos en Stock Bajo**")
        if len(productos_bajos) > 0:
            st.warning(f"**{len(productos_bajos)} productos necesitan reposición pronto**")
            for _, prod in productos_bajos.iterrows():
                grupo_prod = prod['Grupo_Nombre']
                st.markdown(f"• {prod['descripcion']} ({grupo_prod})")
        else:
            st.success("✅ No hay productos con stock bajo")
    
    with col3:
        st.markdown("**🔵 Productos con Exceso**")
        if len(productos_exceso) > 0:
            st.info(f"**{len(productos_exceso)} productos tienen mucho stock**")
            for _, prod in productos_exceso.iterrows():
                grupo_prod = prod['Grupo_Nombre']
                st.markdown(f"• {prod['descripcion']} ({grupo_prod})")
        else:
            st.success("✅ No hay productos con exceso")
    
    # Recomendaciones específicas por alertas
    st.markdown("**💡 Recomendaciones Específicas:**")
    
    if len(productos_criticos) > 0:
        grupos_criticos = productos_criticos['Grupo_Nombre'].unique()
        st.error(f"🚨 **Acción Inmediata:** Los grupos {', '.join(grupos_criticos)} contienen productos críticos")
    
    if len(productos_bajos) > 0:
        grupos_bajos = productos_bajos['Grupo_Nombre'].unique()
        st.warning(f"⚠️ **Planificar:** Los grupos {', '.join(grupos_bajos)} necesitan reposición en breve")
    
    if len(productos_exceso) > 0:
        grupos_exceso = productos_exceso['Grupo_Nombre'].unique()
        st.info(f"📦 **Optimizar:** Los grupos {', '.join(grupos_exceso)} tienen exceso de inventario")

except Exception as e:
    st.error(f"❌ Error al procesar los datos: {str(e)}")
    st.info("Asegúrese de que el archivo de inventario esté disponible")
    st.code("""
    Estructura esperada:
    sunmarket-dashboard/
    ├── data/
    │   └── dias_inventario.csv
    └── pages/
        └── 03_ml.py
    """)

# Footer
st.markdown("---")
st.markdown("*Análisis Inteligente de Productos - SunMarket Dashboard*")
