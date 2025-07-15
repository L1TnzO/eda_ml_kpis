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

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_inventory_data

# Configuración de la página
st.set_page_config(
    page_title="ML Analysis",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Machine Learning Analysis - SunMarket")
st.markdown("---")

# Cargar datos
try:
    datos = load_inventory_data()
    st.success(f"✅ Datos cargados exitosamente: {len(datos)} productos")
    
    # Sidebar con configuración de ML
    st.sidebar.header("⚙️ Configuración ML")
    
    # Selección de características
    available_features = ['stock_actual', 'dias_con_ventas', 'venta_promedio_diaria', 'dias_inventario_disponible']
    
    use_features = st.sidebar.multiselect(
        "Características para clustering:",
        available_features,
        default=['stock_actual', 'venta_promedio_diaria', 'dias_inventario_disponible'],
        help="Selecciona las variables para el análisis de clustering"
    )
    
    if len(use_features) < 2:
        st.error("❌ Selecciona al menos 2 características para el análisis")
        st.stop()
    
    # Configuración de clustering
    n_clusters = st.sidebar.slider(
        "Número de clusters:", 
        min_value=2, 
        max_value=min(8, len(datos)), 
        value=4,
        help="Número de grupos para el clustering K-means"
    )
    
    # Configuración de PCA
    show_pca_details = st.sidebar.checkbox(
        "Mostrar detalles PCA", 
        value=True,
        help="Mostrar información detallada sobre los componentes principales"
    )
    
    # Preparar datos para ML
    @st.cache_data
    def prepare_ml_data(features, n_clusters):
        # Seleccionar características
        X = datos[features].copy()
        
        # Verificar valores nulos
        if X.isnull().any().any():
            st.warning("⚠️ Se encontraron valores nulos, se rellenarán con la media")
            X = X.fillna(X.mean())
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Clustering K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # PCA para visualización
        pca = PCA(n_components=min(2, len(features)))
        X_pca = pca.fit_transform(X_scaled)
        
        # Métricas de clustering
        silhouette_avg = silhouette_score(X_scaled, clusters)
        inertia = kmeans.inertia_
        
        return X, X_scaled, clusters, X_pca, kmeans, pca, scaler, silhouette_avg, inertia
    
    X, X_scaled, clusters, X_pca, kmeans, pca, scaler, silhouette_avg, inertia = prepare_ml_data(use_features, n_clusters)
    
    # Métricas de calidad del clustering
    st.subheader("📊 Métricas de Calidad del Clustering")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Silhouette Score", f"{silhouette_avg:.3f}", help="Calidad del clustering (0-1, mejor cerca de 1)")
    
    with col2:
        st.metric("Inertia", f"{inertia:.2f}", help="Suma de distancias al cuadrado dentro de clusters")
    
    with col3:
        st.metric("Clusters", n_clusters, help="Número de grupos identificados")
    
    with col4:
        st.metric("Características", len(use_features), help="Variables utilizadas en el análisis")
    
    # Interpretación de métricas
    if silhouette_avg > 0.7:
        st.success("✅ Excelente calidad de clustering")
    elif silhouette_avg > 0.5:
        st.info("ℹ️ Buena calidad de clustering")
    elif silhouette_avg > 0.3:
        st.warning("⚠️ Calidad moderada de clustering")
    else:
        st.error("❌ Calidad baja de clustering - considera ajustar parámetros")
    
    # Visualización PCA
    st.subheader("📊 Visualización del Clustering (Proyección PCA)")
    
    # Crear DataFrame para visualización
    df_pca = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1] if X_pca.shape[1] > 1 else X_pca[:, 0],
        'Cluster': clusters.astype(str),
        'Producto': datos['descripcion'],
        'Alerta_Stock': datos['alerta_stock']
    })
    
    # Agregar características originales al hover
    for feature in use_features:
        df_pca[feature] = datos[feature]
    
    # Crear gráfico PCA
    fig_pca = px.scatter(
        df_pca, 
        x='PC1', 
        y='PC2', 
        color='Cluster',
        hover_data=['Producto', 'Alerta_Stock'] + use_features,
        title=f"Clustering de Productos - Proyección PCA ({len(use_features)} características)",
        labels={'PC1': f'Componente Principal 1', 'PC2': f'Componente Principal 2'}
    )
    
    # Personalizar el gráfico
    fig_pca.update_traces(marker=dict(size=10, opacity=0.8))
    fig_pca.update_layout(
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig_pca, use_container_width=True)
    
    # Detalles de PCA
    if show_pca_details and len(use_features) > 1:
        st.subheader("📈 Análisis de Componentes Principales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Varianza explicada
            explained_variance = pca.explained_variance_ratio_
            
            fig_variance = px.bar(
                x=[f'PC{i+1}' for i in range(len(explained_variance))],
                y=explained_variance,
                title="Varianza Explicada por Componente",
                labels={'x': 'Componente Principal', 'y': 'Varianza Explicada'}
            )
            fig_variance.update_traces(marker_color='lightblue')
            st.plotly_chart(fig_variance, use_container_width=True)
            
            st.info(f"**Varianza total explicada:** {explained_variance.sum():.1%}")
        
        with col2:
            # Contribución de características
            components_df = pd.DataFrame({
                'Característica': use_features,
                'PC1': pca.components_[0],
                'PC2': pca.components_[1] if len(pca.components_) > 1 else np.zeros(len(use_features))
            })
            
            fig_components = px.bar(
                components_df, 
                x='Característica', 
                y=['PC1', 'PC2'],
                title="Contribución de Características a los Componentes",
                labels={'value': 'Contribución', 'variable': 'Componente'}
            )
            fig_components.update_xaxes(tickangle=45)
            st.plotly_chart(fig_components, use_container_width=True)
    
    # Análisis por cluster
    st.subheader("🎯 Análisis Detallado por Cluster")
    
    # Crear DataFrame con clusters
    datos_con_clusters = datos.copy()
    datos_con_clusters['Cluster'] = clusters
    
    # Estadísticas por cluster
    cluster_stats = datos_con_clusters.groupby('Cluster')[use_features].agg(['mean', 'std', 'count']).round(2)
    
    # Mostrar estadísticas
    st.markdown("**📊 Estadísticas por Cluster:**")
    st.dataframe(cluster_stats, use_container_width=True)
    
    # Visualización de distribución por cluster
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de productos por cluster
        cluster_counts = datos_con_clusters['Cluster'].value_counts().sort_index()
        
        fig_dist = px.bar(
            x=cluster_counts.index.astype(str),
            y=cluster_counts.values,
            title="Distribución de Productos por Cluster",
            labels={'x': 'Cluster', 'y': 'Número de Productos'},
            color=cluster_counts.values,
            color_continuous_scale='viridis'
        )
        fig_dist.update_layout(showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Distribución de alertas por cluster
        alert_by_cluster = datos_con_clusters.groupby(['Cluster', 'alerta_stock']).size().unstack(fill_value=0)
        
        fig_alert = px.bar(
            alert_by_cluster, 
            title="Distribución de Alertas por Cluster",
            labels={'value': 'Número de Productos', 'index': 'Cluster'},
            color_discrete_map={
                'CRÍTICO': '#ff4444',
                'BAJO': '#ffaa00',
                'NORMAL': '#44ff44',
                'EXCESO': '#0088ff'
            }
        )
        st.plotly_chart(fig_alert, use_container_width=True)
    
    # Análisis detallado por cluster
    st.subheader("🔍 Perfiles de Clusters")
    
    # Crear tabs para cada cluster
    cluster_tabs = st.tabs([f"Cluster {i}" for i in range(n_clusters)])
    
    for i, tab in enumerate(cluster_tabs):
        with tab:
            cluster_data = datos_con_clusters[datos_con_clusters['Cluster'] == i]
            
            if len(cluster_data) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🏷️ Productos en Cluster {i} ({len(cluster_data)} productos):**")
                    
                    # Mostrar productos
                    productos_cluster = cluster_data[['descripcion', 'alerta_stock'] + use_features].sort_values('dias_inventario_disponible')
                    st.dataframe(productos_cluster, use_container_width=True)
                
                with col2:
                    st.markdown(f"**📊 Características promedio del Cluster {i}:**")
                    
                    # Estadísticas del cluster
                    for feature in use_features:
                        avg_value = cluster_data[feature].mean()
                        std_value = cluster_data[feature].std()
                        st.write(f"• **{feature}**: {avg_value:.2f} ± {std_value:.2f}")
                    
                    # Distribución de alertas
                    st.markdown("**⚠️ Distribución de alertas:**")
                    alert_dist = cluster_data['alerta_stock'].value_counts()
                    for alert, count in alert_dist.items():
                        percentage = (count / len(cluster_data)) * 100
                        st.write(f"• {alert}: {count} productos ({percentage:.1f}%)")
    
    # Interpretación y recomendaciones
    st.subheader("💡 Interpretación y Recomendaciones")
    
    # Análisis automático de clusters
    interpretaciones = []
    
    for i in range(n_clusters):
        cluster_data = datos_con_clusters[datos_con_clusters['Cluster'] == i]
        
        if len(cluster_data) > 0:
            avg_dias = cluster_data['dias_inventario_disponible'].mean()
            avg_stock = cluster_data['stock_actual'].mean()
            avg_venta = cluster_data['venta_promedio_diaria'].mean()
            
            if avg_dias < 20:
                tipo = "🔥 Alta Rotación"
                recomendacion = "Monitorear stock frecuentemente, posible aumento de pedidos"
            elif avg_dias > 60:
                tipo = "🐌 Baja Rotación"
                recomendacion = "Evaluar descuentos o descontinuación, reducir pedidos"
            else:
                tipo = "⚖️ Rotación Media"
                recomendacion = "Mantener nivel actual, revisar estacionalidad"
            
            interpretaciones.append({
                'cluster': i,
                'tipo': tipo,
                'productos': len(cluster_data),
                'dias_promedio': avg_dias,
                'recomendacion': recomendacion
            })
    
    # Mostrar interpretaciones
    for interp in interpretaciones:
        st.info(f"""
        **Cluster {interp['cluster']} - {interp['tipo']}**
        - Productos: {interp['productos']}
        - Días promedio de inventario: {interp['dias_promedio']:.1f}
        - Recomendación: {interp['recomendacion']}
        """)
    
    # Recomendaciones generales
    st.subheader("🎯 Recomendaciones Estratégicas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **📈 Optimización de Inventario:**
        - Ajustar frecuencia de pedidos según cluster
        - Implementar alertas automáticas por grupo
        - Revisar políticas de descuentos por cluster
        - Considerar estacionalidad en la clasificación
        """)
    
    with col2:
        st.warning("""
        **🔍 Monitoreo Continuo:**
        - Recalcular clusters mensualmente
        - Validar cambios en comportamiento
        - Ajustar número de clusters según crecimiento
        - Incorporar nuevas variables relevantes
        """)
    
    # Limitaciones y consideraciones éticas
    st.subheader("⚠️ Limitaciones y Consideraciones Éticas")
    
    st.error("""
    **🚨 Limitaciones Críticas:**
    - **Datos sintéticos**: Los patrones no reflejan comportamiento real de consumidores
    - **Muestra pequeña**: 26 productos pueden no ser representativos
    - **Falta de contexto**: No considera factores externos (estacionalidad, promociones, competencia)
    - **Clustering puede cambiar**: Resultados sensibles a nuevos datos
    
    **⚖️ Consideraciones Éticas:**
    - **No automatizar decisiones**: El análisis debe ser revisado por expertos
    - **Validación necesaria**: Probar con datos reales antes de implementar
    - **Impacto en empleados**: Considerar efectos en personal de ventas
    - **Transparencia**: Explicar criterios de clasificación a stakeholders
    
    **🎯 Uso Responsable:**
    - Complementar con análisis de rentabilidad
    - Considerar impacto en satisfacción del cliente
    - Evaluar recursos necesarios para implementación
    - Monitorear efectos no deseados
    """)

except Exception as e:
    st.error(f"❌ Error al cargar o procesar los datos: {str(e)}")
    st.info("Verifica que el archivo 'dias_inventario.csv' esté en la carpeta 'data/'")
    st.code(f"Error específico: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Machine Learning Analysis - SunMarket Analytics Dashboard*")
