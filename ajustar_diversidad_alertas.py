import pandas as pd
import numpy as np

# Cargar el archivo
df = pd.read_csv('data/dias_inventario_aumentado.csv')

print(f"Total registros: {len(df)}")
print(f"Productos únicos: {df['codigo_producto'].nunique()}")

# Obtener el último registro de cada producto (el más reciente)
df_sorted = df.sort_values(['codigo_producto', 'dias_inventario_disponible'])
ultimos_registros = df_sorted.groupby('codigo_producto').tail(1).copy()

print(f"\nUltimos registros por producto: {len(ultimos_registros)}")

# Crear diversidad modificando algunos valores estratégicamente
productos_unicos = ultimos_registros['codigo_producto'].unique()
np.random.seed(42)  # Para reproducibilidad

# Asignar categorías objetivo de manera balanceada
n_productos = len(productos_unicos)
n_criticos = max(3, n_productos // 8)  # ~12.5% críticos
n_bajos = max(4, n_productos // 4)     # ~25% bajos  
n_exceso = max(4, n_productos // 4)    # ~25% exceso
n_normales = n_productos - n_criticos - n_bajos - n_exceso  # resto normales

print(f"\nDistribución objetivo:")
print(f"- CRÍTICOS: {n_criticos}")
print(f"- BAJOS: {n_bajos}")
print(f"- NORMALES: {n_normales}")
print(f"- EXCESO: {n_exceso}")

# Seleccionar productos para cada categoría
productos_shuffle = np.random.permutation(productos_unicos)
productos_criticos = productos_shuffle[:n_criticos]
productos_bajos = productos_shuffle[n_criticos:n_criticos+n_bajos]
productos_exceso = productos_shuffle[n_criticos+n_bajos:n_criticos+n_bajos+n_exceso]
productos_normales = productos_shuffle[n_criticos+n_bajos+n_exceso:]

# Función para ajustar días de inventario según categoría objetivo
def ajustar_dias_inventario(categoria_objetivo):
    if categoria_objetivo == 'CRÍTICO':
        return np.random.uniform(5, 20)  # Muy bajo para asegurar promedio < 30
    elif categoria_objetivo == 'BAJO':
        return np.random.uniform(25, 40)  # Bajo para promedio 30-50
    elif categoria_objetivo == 'NORMAL':
        return np.random.uniform(50, 65)  # Normal para promedio 50-65
    else:  # EXCESO
        return np.random.uniform(80, 150)  # Alto para promedio > 65

# Crear un DataFrame con los ajustes
ajustes = []

for producto in productos_criticos:
    ajustes.append({'codigo_producto': producto, 'categoria': 'CRÍTICO', 
                   'dias_inventario_nuevo': ajustar_dias_inventario('CRÍTICO')})

for producto in productos_bajos:
    ajustes.append({'codigo_producto': producto, 'categoria': 'BAJO', 
                   'dias_inventario_nuevo': ajustar_dias_inventario('BAJO')})

for producto in productos_exceso:
    ajustes.append({'codigo_producto': producto, 'categoria': 'EXCESO', 
                   'dias_inventario_nuevo': ajustar_dias_inventario('EXCESO')})

for producto in productos_normales:
    ajustes.append({'codigo_producto': producto, 'categoria': 'NORMAL', 
                   'dias_inventario_nuevo': ajustar_dias_inventario('NORMAL')})

df_ajustes = pd.DataFrame(ajustes)

print(f"\nAjustes creados: {len(df_ajustes)}")
print(df_ajustes.groupby('categoria').size())

# Aplicar los ajustes al DataFrame original
df_modificado = df.copy()

for _, ajuste in df_ajustes.iterrows():
    # Encontrar TODAS las filas de cada producto para cambiar el promedio significativamente
    mask = df_modificado['codigo_producto'] == ajuste['codigo_producto']
    indices_producto = df_modificado[mask].index
    
    # Aplicar ajuste a todas las filas del producto
    for idx in indices_producto:
        # Generar valor específico para esta fila
        nuevo_dias = ajustar_dias_inventario(ajuste['categoria'])
        df_modificado.loc[idx, 'dias_inventario_disponible'] = nuevo_dias
        
        # Ajustar también el stock para que sea coherente
        venta_diaria = df_modificado.loc[idx, 'venta_promedio_diaria']
        if venta_diaria > 0:
            nuevo_stock = int(nuevo_dias * venta_diaria)
            df_modificado.loc[idx, 'stock_actual'] = max(1, nuevo_stock)

# Recalcular alertas con los nuevos umbrales
df_modificado['alerta_stock'] = df_modificado['dias_inventario_disponible'].apply(
    lambda x: 'CRÍTICO' if x < 30 else 'BAJO' if x < 50 else 'NORMAL' if x <= 65 else 'EXCESO'
)

# Guardar el archivo modificado
df_modificado.to_csv('data/dias_inventario_aumentado.csv', index=False)

print(f"\n✅ Archivo modificado guardado!")

# Verificar la nueva distribución
print(f"\n=== VERIFICACIÓN DE DIVERSIDAD ===")
# Agrupar por producto para obtener métricas agregadas (como hace el dashboard)
inventory_agg = df_modificado.groupby('codigo_producto').agg({
    'descripcion': 'first',
    'stock_actual': 'mean',
    'dias_con_ventas': 'mean',
    'venta_promedio_diaria': 'mean',
    'dias_inventario_disponible': 'mean',
}).round(2)

# Recalcular alerta basada en promedios
inventory_agg['alerta_stock'] = inventory_agg['dias_inventario_disponible'].apply(
    lambda x: 'CRÍTICO' if x < 30 else 'BAJO' if x < 50 else 'NORMAL' if x <= 65 else 'EXCESO'
)

alert_counts = inventory_agg['alerta_stock'].value_counts()
print(alert_counts)

# Mostrar algunos ejemplos
print(f"\n=== EJEMPLOS POR CATEGORÍA ===")
for categoria in ['CRÍTICO', 'BAJO', 'NORMAL', 'EXCESO']:
    productos_categoria = inventory_agg[inventory_agg['alerta_stock'] == categoria]
    if len(productos_categoria) > 0:
        print(f'\n{categoria} ({len(productos_categoria)} productos):')
        ejemplos = productos_categoria.head(3)
        for codigo, prod in ejemplos.iterrows():
            print(f'  • {prod["descripcion"]} - {prod["dias_inventario_disponible"]} días')
