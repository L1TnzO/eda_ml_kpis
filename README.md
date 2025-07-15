# SunMarket Analytics Dashboard

Dashboard interactivo para análisis de datos de SunMarket utilizando la capa Gold del Data Lake.

## 🎯 Objetivo

Crear un producto web que incluya:
- ✅ **EDA** de tabla específica (inventario)
- ✅ **KPIs temporales** (ventas, transacciones, venta promedio)
- ✅ **Análisis ML** (clustering y proyección PCA)

## 🚀 Instalación Rápida

### 1. Clonar/Acceder al proyecto
```bash
cd sunmarket-dashboard
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar aplicación
```bash
streamlit run app.py
```

## 📊 Funcionalidades

### Página Principal
- Métricas principales del negocio
- Resumen ejecutivo con gráficos
- Navegación intuitiva

### 1. 📊 EDA - Inventario
- Análisis exploratorio de datos de inventario
- Estadísticas descriptivas
- Visualizaciones interactivas:
  - Distribución de días de inventario
  - Niveles de alerta de stock
  - Correlaciones entre variables
  - Productos críticos y de alta/baja rotación

### 2. 📈 KPIs Temporales
- Evolución temporal de 3 KPIs principales:
  - **Ventas diarias**: Monto total por día
  - **Transacciones diarias**: Número de operaciones
  - **Venta promedio**: Valor por transacción
- Filtros de fecha interactivos
- Análisis de correlación y tendencias

### 3. 🤖 ML Analysis
- Clustering K-means de productos
- Proyección PCA para visualización
- Configuración interactiva:
  - Selección de características
  - Número de clusters
  - Método de escalado
- Métricas de calidad (Silhouette Score)
- Interpretación y recomendaciones

## 📁 Estructura del Proyecto

```
sunmarket-dashboard/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── README.md             # Documentación
├── .streamlit/
│   └── config.toml       # Configuración de Streamlit
├── data/                 # Datos de la capa gold
│   ├── dias_inventario.csv
│   ├── transacciones_diarias.csv
│   └── ventas_diarias.csv
├── pages/                # Páginas del dashboard
│   ├── 01_eda.py        # EDA de inventario
│   ├── 02_temporal_kpis.py # KPIs temporales
│   └── 03_ml_analysis.py   # Análisis ML
└── utils/                # Utilidades
    └── data_loader.py    # Carga de datos
```

## 🛠️ Tecnologías Utilizadas

- **Streamlit**: Framework web para Python
- **Pandas**: Manipulación de datos
- **Plotly**: Visualizaciones interactivas
- **Scikit-learn**: Machine Learning
- **NumPy**: Computación numérica

## 📈 Datos

Los datos provienen de la capa Gold del Data Lake de SunMarket:

- **dias_inventario.csv**: Análisis de rotación de 26 productos
- **transacciones_diarias.csv**: 202 días de actividad transaccional
- **ventas_diarias.csv**: 202 días de datos de ventas (2023)

## 🎨 Características del Dashboard

- **Responsive**: Adaptable a diferentes tamaños de pantalla
- **Interactivo**: Filtros y controles dinámicos
- **Informativo**: Métricas y estadísticas clave
- **Intuitivo**: Navegación clara y organizada
- **Completo**: Cumple todos los requisitos de evaluación

## ⚠️ Consideraciones Importantes

### Limitaciones
- Los datos son sintéticos (generados artificialmente)
- Muestra limitada (26 productos, 202 días)
- No incluye factores externos (estacionalidad, promociones)

### Consideraciones Éticas
- Advertencias sobre naturaleza sintética de los datos
- Recomendaciones para validación con datos reales
- Transparencia en limitaciones del análisis

## 📝 Cumplimiento de Requisitos

### Requisitos Técnicos ✅
- [x] Producto web funcional
- [x] EDA de tabla específica (inventario)
- [x] Gráfico de variabilidad temporal (3 KPIs)
- [x] Análisis ML (clustering K-means)

### Criterios de Evaluación ✅
- [x] Datos relevantes de capa gold
- [x] Técnicas analíticas apropiadas
- [x] Responde a objetivos planteados
- [x] Visualizaciones útiles y estructuradas
- [x] Navegación clara y lógica
- [x] Identificación de limitaciones

## 🚀 Despliegue

Para desplegar en producción:

1. Configurar servidor con Python 3.8+
2. Instalar dependencias
3. Configurar puerto (por defecto 8501)
4. Ejecutar: `streamlit run app.py`

## 👥 Equipo

Desarrollado para el curso de Ingeniería de Datos - Universidad.

---

*Dashboard creado con Streamlit para análisis de datos de SunMarket*
