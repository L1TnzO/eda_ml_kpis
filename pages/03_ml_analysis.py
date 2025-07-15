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

# Suprimir warnings de NumPy para mejor experiencia del usuario
warnings.filterwarnings('ignore', category=RuntimeWarning)
np.seterr(divide='ignore', invalid='ignore')

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
st.markdown("**Análisis avanzado con clustering y proyección dimensional**")

# Cargar datos
try:
    datos = load_inventory_data()
    st.success(f"✅ Datos cargados: {len(datos)} productos para análisis ML")
    
    # Configuración de ML en sidebar
    st.sidebar.header("⚙️ Configuración del Análisis ML")
    
    # Selección de características
    available_features = ['stock_actual', 'dias_con_ventas', 'venta_promedio_diaria', 'dias_inventario_disponible']
    selected_features = st.sidebar.multiselect(
        "Características para clustering:",
        available_features,
        default=['stock_actual', 'venta_promedio_diaria', 'dias_inventario_disponible'],
        help="Selecciona las variables que se usarán para el clustering"
    )
    
    # Validación de características seleccionadas
    if len(selected_features) < 2:
        st.error("❌ Selecciona al menos 2 características para el análisis")
        st.stop()
    
    # Número de clusters
    n_clusters = st.sidebar.slider(
        "Número de clusters:",
        min_value=2,
        max_value=8,
        value=4,
        help="Número de grupos para el clustering K-means"
    )
    
    # Método de escalado
    scaling_method = st.sidebar.selectbox(
        "Método de escalado:",
        ["StandardScaler", "Sin escalar"],
        help="Método para normalizar los datos"
    )
    
    # Preparar datos para ML
    @st.cache_data
    def prepare_ml_data(features, n_clusters, scaling_method):
        X = datos[features].copy()
        
        # Verificar valores nulos
        if X.isnull().any().any():
            st.warning("⚠️ Hay valores nulos en los datos. Se rellenarán con la media.")
            X = X.fillna(X.mean())
        
        # Escalar datos
        if scaling_method == "StandardScaler":
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
        else:
            scaler = None
            X_scaled = X.values
        
        # Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # PCA para visualización
        pca = PCA(n_components=min(2, len(features)))
        X_pca = pca.fit_transform(X_scaled)
        
        # Métricas
        silhouette_avg = silhouette_score(X_scaled, clusters)
        inertia = kmeans.inertia_
        
        return X, X_scaled, clusters, X_pca, kmeans, pca, scaler, silhouette_avg, inertia
    
    X, X_scaled, clusters, X_pca, kmeans, pca, scaler, silhouette_avg, inertia = prepare_ml_data(
        selected_features, n_clusters, scaling_method
    )
    
    # Métricas de calidad del clustering
    st.subheader("📊 Métricas de Calidad del Clustering")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Silhouette Score",
            f"{silhouette_avg:.3f}",
            help="Mide qué tan bien separados están los clusters (0-1, mayor es mejor)"
        )
    
    with col2:
        st.metric(
            "Inercia",
            f"{inertia:.0f}",
            help="Suma de distancias al cuadrado dentro de clusters (menor es mejor)"
        )
    
    with col3:
        st.metric(
            "Número de Clusters",
            f"{n_clusters}",
            help="Número de grupos creados"
        )
    
    with col4:
        st.metric(
            "Características",
            f"{len(selected_features)}",
            help="Número de variables utilizadas"
        )
    
    # Visualización PCA
    st.subheader("📈 Visualización del Clustering (Proyección PCA)")
    
    # Crear DataFrame para visualización
    df_pca = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1] if X_pca.shape[1] > 1 else X_pca[:, 0],
        'Cluster': clusters,
        'Producto': datos['descripcion'],
        'Alerta_Stock': datos['alerta_stock']
    })
    
    # Agregar información adicional al hover
    for feature in selected_features:
        df_pca[feature] = datos[feature]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Gráfico PCA principal
        fig_pca = px.scatter(
            df_pca,
            x='PC1',
            y='PC2',
            color='Cluster',
            size='stock_actual' if 'stock_actual' in selected_features else None,
            hover_data=['Producto', 'Alerta_Stock'] + selected_features,
            title="Clustering de Productos - Proyección PCA",
            labels={
                'PC1': f'PC1 ({pca.explained_variance_ratio_[0]:.1%} varianza)',
                'PC2': f'PC2 ({pca.explained_variance_ratio_[1]:.1%} varianza)' if X_pca.shape[1] > 1 else 'PC1'
            }
        )
        
        # Agregar centroides
        if scaler:
            centroids_original = scaler.inverse_transform(kmeans.cluster_centers_)
            centroids_pca = pca.transform(kmeans.cluster_centers_)
        else:
            centroids_pca = pca.transform(kmeans.cluster_centers_)
        
        fig_pca.add_trace(go.Scatter(
            x=centroids_pca[:, 0],
            y=centroids_pca[:, 1] if centroids_pca.shape[1] > 1 else centroids_pca[:, 0],
            mode='markers',
            marker=dict(
                size=15,
                symbol='x',
                color='red',
                line=dict(width=2, color='black')
            ),
            name='Centroides',
            showlegend=True
        ))
        
        st.plotly_chart(fig_pca, use_container_width=True)
    
    with col2:
        # Información sobre los componentes principales
        st.markdown("**📊 Información PCA:**")
        
        if X_pca.shape[1] > 1:
            st.write(f"**PC1:** {pca.explained_variance_ratio_[0]:.1%} varianza")
            st.write(f"**PC2:** {pca.explained_variance_ratio_[1]:.1%} varianza")
            st.write(f"**Total explicado:** {pca.explained_variance_ratio_[:2].sum():.1%}")
        else:
            st.write(f"**PC1:** {pca.explained_variance_ratio_[0]:.1%} varianza")
        
        st.markdown("**🎯 Interpretación:**")
        st.write("- Puntos del mismo color pertenecen al mismo cluster")
        st.write("- Las 'X' rojas son los centroides")
        st.write("- Distancia = similitud entre productos")
    
    # Explicación de componentes principales
    st.subheader("🔍 Contribución de Características a los Componentes")
    
    components_df = pd.DataFrame({
        'Característica': selected_features,
        'PC1': pca.components_[0],
        'PC2': pca.components_[1] if pca.components_.shape[0] > 1 else pca.components_[0]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_components = px.bar(
            components_df,
            x='Característica',
            y=['PC1', 'PC2'] if pca.components_.shape[0] > 1 else ['PC1'],
            title="Contribución de Características a los Componentes",
            barmode='group'
        )
        fig_components.update_layout(
            xaxis_title="Características",
            yaxis_title="Contribución",
            showlegend=True
        )
        st.plotly_chart(fig_components, use_container_width=True)
    
    with col2:
        st.markdown("**🔍 Interpretación:**")
        st.write("- Valores positivos y negativos indican dirección de la contribución")
        st.write("- Barras más altas = mayor influencia en el componente")
        st.write("- PC1 explica la mayor variabilidad")
        st.write("- PC2 explica la segunda mayor variabilidad")
    
    # Análisis por cluster
    st.subheader("🎯 Análisis Detallado por Cluster")
    
    # Crear DataFrame con clusters
    datos_con_clusters = datos.copy()
    datos_con_clusters['Cluster'] = clusters
    
    # Estadísticas por cluster
    cluster_stats = datos_con_clusters.groupby('Cluster')[selected_features].agg(['mean', 'count', 'std']).round(2)
    
    # Visualizar distribución de productos por cluster
    col1, col2 = st.columns(2)
    
    with col1:
        cluster_counts = pd.Series(clusters).value_counts().sort_index()
        fig_cluster_dist = px.bar(
            x=cluster_counts.index,
            y=cluster_counts.values,
            title="Distribución de Productos por Cluster",
            labels={'x': 'Cluster', 'y': 'Número de Productos'}
        )
        fig_cluster_dist.update_traces(
            text=cluster_counts.values,
            textposition='outside'
        )
        st.plotly_chart(fig_cluster_dist, use_container_width=True)
    
    with col2:
        # Distribución de alertas por cluster
        alert_cluster = pd.crosstab(datos_con_clusters['Cluster'], datos_con_clusters['alerta_stock'])
        fig_alert_cluster = px.bar(
            alert_cluster,
            title="Distribución de Alertas por Cluster",
            labels={'value': 'Número de Productos', 'index': 'Cluster'}
        )
        st.plotly_chart(fig_alert_cluster, use_container_width=True)
    
    # Características detalladas de cada cluster
    st.subheader("📋 Características Detalladas por Cluster")
    
    for cluster_id in range(n_clusters):
        cluster_data = datos_con_clusters[datos_con_clusters['Cluster'] == cluster_id]
        
        with st.expander(f"🔍 Cluster {cluster_id} - {len(cluster_data)} productos"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Productos en este cluster:**")
                productos_cluster = cluster_data[['descripcion', 'alerta_stock'] + selected_features]
                st.dataframe(productos_cluster)
            
            with col2:
                st.markdown("**Estadísticas del cluster:**")
                for feature in selected_features:
                    media = cluster_data[feature].mean()
                    std = cluster_data[feature].std()
                    st.write(f"**{feature}:**")
                    st.write(f"  - Media: {media:.2f}")
                    st.write(f"  - Desv. estándar: {std:.2f}")
                
                # Distribución de alertas en el cluster
                st.markdown("**Distribución de alertas:**")
                alert_dist = cluster_data['alerta_stock'].value_counts()
                for alert, count in alert_dist.items():
                    st.write(f"  - {alert}: {count} productos")
    
    # Interpretación y recomendaciones
    st.subheader("💡 Interpretación y Recomendaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🎯 Interpretación del Clustering:**
        
        El análisis de clustering revela grupos naturales de productos basados en sus características de inventario y ventas:
        
        - **Productos similares** se agrupan juntos
        - **Patrones de comportamiento** se identifican automáticamente
        - **Segmentación objetiva** basada en datos
        - **Estrategias diferenciadas** por cluster
        """)
    
    with col2:
        st.success("""
        **📈 Recomendaciones por Cluster:**
        
        - **Cluster 0**: Monitoreo frecuente si predominan productos críticos
        - **Cluster 1**: Estrategia de promociones si hay exceso de stock
        - **Cluster 2**: Optimización de reposición para productos normales
        - **Cluster 3**: Análisis individual si hay patrones únicos
        
        *Adapta las estrategias según las características específicas de cada cluster*
        """)
    
    # Análisis de la calidad del clustering
    st.subheader("📊 Evaluación de la Calidad del Clustering")
    
    # Método del codo para encontrar el número óptimo de clusters
    @st.cache_data
    def elbow_analysis(X_scaled, max_k=8):
        inertias = []
        silhouette_scores = []
        k_range = range(2, min(max_k + 1, len(X_scaled)))
        
        for k in k_range:
            kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
            clusters_temp = kmeans_temp.fit_predict(X_scaled)
            inertias.append(kmeans_temp.inertia_)
            silhouette_scores.append(silhouette_score(X_scaled, clusters_temp))
        
        return k_range, inertias, silhouette_scores
    
    k_range, inertias, silhouette_scores = elbow_analysis(X_scaled)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Método del codo
        fig_elbow = px.line(
            x=list(k_range),
            y=inertias,
            markers=True,
            title="Método del Codo",
            labels={'x': 'Número de Clusters', 'y': 'Inercia'}
        )
        fig_elbow.add_vline(x=n_clusters, line_dash="dash", line_color="red", 
                           annotation_text=f"Actual: {n_clusters}")
        st.plotly_chart(fig_elbow, use_container_width=True)
    
    with col2:
        # Análisis de silhouette
        fig_silhouette = px.line(
            x=list(k_range),
            y=silhouette_scores,
            markers=True,
            title="Análisis de Silhouette",
            labels={'x': 'Número de Clusters', 'y': 'Silhouette Score'}
        )
        fig_silhouette.add_vline(x=n_clusters, line_dash="dash", line_color="red",
                                annotation_text=f"Actual: {n_clusters}")
        st.plotly_chart(fig_silhouette, use_container_width=True)
    
    # Consideraciones éticas y limitaciones
    st.subheader("⚠️ Consideraciones Éticas y Limitaciones")
    
    st.warning("""
    **⚠️ Limitaciones del Análisis ML:**
    
    - **Datos sintéticos**: Los resultados pueden no reflejar patrones reales de negocio
    - **Muestra limitada**: Solo 26 productos pueden no ser representativos
    - **Clustering no supervisado**: Los grupos pueden no tener significado comercial directo
    - **Interpretación subjetiva**: Los resultados requieren validación con conocimiento de negocio
    
    **🔒 Consideraciones Éticas:**
    
    - **Transparencia**: El modelo debe ser explicable para stakeholders
    - **Sesgo de datos**: Los datos artificiales pueden introducir sesgos no intencionados
    - **Decisiones automatizadas**: No usar como única base para decisiones críticas
    - **Validación humana**: Siempre validar resultados con expertos en el dominio
    
    **📋 Recomendaciones de Uso:**
    
    - Usar como herramienta exploratoria, no decisoria
    - Validar con datos reales antes de implementar estrategias
    - Complementar con análisis de negocio tradicional
    - Revisar y actualizar regularmente el modelo
    """)

except Exception as e:
    st.error(f"❌ Error al cargar o procesar los datos: {str(e)}")
    st.info("Asegúrate de que el archivo 'dias_inventario.csv' esté en la carpeta 'data/' y que todas las dependencias estén instaladas.")
    st.code("""
    Dependencias requeridas:
    - streamlit
    - pandas
    - plotly
    - scikit-learn
    - numpy
    """)

# Footer
st.markdown("---")
st.markdown("*Análisis ML - SunMarket Analytics Dashboard*")
