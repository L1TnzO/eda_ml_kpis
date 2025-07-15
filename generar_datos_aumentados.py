import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os

def calcular_alerta(dias):
    """Calcula el nivel de alerta basado en días de inventario"""
    if dias < 7:
        return 'CRÍTICO'
    elif 7 <= dias < 30:
        return 'BAJO'
    elif 30 <= dias <= 90:
        return 'NORMAL'
    else:
        return 'EXCESO'

def reabastecer(stock_actual, stock_min, stock_max):
    """Si el stock está bajo, se reabastece con valor aleatorio entre min y max"""
    return np.random.randint(stock_min, stock_max + 1)

def generar_datos_inventario_por_fecha(fila, fechas_mensuales):
    """Genera datos históricos de inventario para un producto específico"""
    historial = []
    
    codigo = fila['codigo_producto']
    descripcion = fila['descripcion']
    stock_inicial = fila['stock_actual']
    venta_diaria_base = fila['venta_promedio_diaria']
    dias_ventas_base = fila['dias_con_ventas']
    
    # Calcular stock min/max por producto
    stock_min = int(venta_diaria_base * 15)  # Stock mínimo (15 días de venta)
    stock_max = int(stock_min * 2.5)  # 2.5 veces el mínimo
    
    for mes in fechas_mensuales:
        # Simular variabilidad en la venta promedio (±25%)
        venta_simulada = venta_diaria_base * np.random.uniform(0.75, 1.25)
        
        # Simular variabilidad en días con ventas (±20%)
        dias_ventas_simulados = max(1, int(dias_ventas_base * np.random.uniform(0.8, 1.2)))
        
        # Calcular stock restante (30 días por mes en promedio)
        consumo_mensual = venta_simulada * 30
        stock_restante = max(stock_inicial - consumo_mensual, 0)
        
        # Recalcular días de inventario
        if venta_simulada > 0:
            dias_inventario = stock_restante / venta_simulada
        else:
            dias_inventario = np.inf if stock_restante > 0 else 0
        
        # Asegurar que no sea infinito
        if dias_inventario == np.inf:
            dias_inventario = 999.0
        
        alerta = calcular_alerta(dias_inventario)
        
        # Reabastecer si es necesario
        if alerta == 'CRÍTICO' or (alerta == 'BAJO' and np.random.random() < 0.7):
            stock_restante = reabastecer(stock_restante, stock_min, stock_max)
            dias_inventario = stock_restante / venta_simulada if venta_simulada > 0 else 999.0
            alerta = calcular_alerta(dias_inventario)
        
        # Guardar datos con los encabezados originales
        historial.append({
            'mes': mes,
            'codigo_producto': codigo,
            'descripcion': descripcion,
            'stock_actual': round(stock_restante, 0),
            'dias_con_ventas': dias_ventas_simulados,
            'venta_promedio_diaria': round(venta_simulada, 2),
            'dias_inventario_disponible': round(dias_inventario, 2),
            'alerta_stock': alerta
        })
        
        # Actualizar stock para el siguiente mes
        stock_inicial = stock_restante
    
    return pd.DataFrame(historial)

def generar_dataset_aumentado():
    """Función principal para generar el dataset aumentado"""
    
    # Cargar datos originales desde la ruta correcta
    archivo_original = '../evaluacion_4/gold/original/recomendados_para_usar_por_profesor/dias_inventario.csv'
    df_original = pd.read_csv(archivo_original)
    print(f"✅ Datos originales cargados: {len(df_original)} productos")
    print(f"📂 Archivo fuente: {archivo_original}")
    
    # Mostrar las columnas disponibles
    print(f"📋 Columnas disponibles: {list(df_original.columns)}")
    
    # Generar lista de meses (2022-2024)
    fecha_inicio = pd.to_datetime('2022-01-01')
    fecha_fin = pd.to_datetime('2024-12-01')
    
    fechas_mensuales = []
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        fechas_mensuales.append(fecha_actual.strftime('%Y-%m'))
        fecha_actual += relativedelta(months=1)
    
    print(f"📅 Generando datos para {len(fechas_mensuales)} meses: {fechas_mensuales[0]} a {fechas_mensuales[-1]}")
    
    # Generar datos históricos para todos los productos
    todos_meses = []
    
    for idx, fila in df_original.iterrows():
        print(f"🔄 Procesando producto {idx+1}/{len(df_original)}: {fila['descripcion']}")
        df_producto_meses = generar_datos_inventario_por_fecha(fila, fechas_mensuales)
        todos_meses.append(df_producto_meses)
    
    # Combinar todo en un solo DataFrame
    df_inventario_aumentado = pd.concat(todos_meses, ignore_index=True)
    
    # Eliminar posibles duplicados
    df_inventario_aumentado = df_inventario_aumentado.drop_duplicates(
        subset=['codigo_producto', 'mes'], 
        keep='first'
    )
    
    print(f"✅ Datos generados: {len(df_inventario_aumentado)} registros")
    
    # Verificaciones
    print("\n📊 Verificaciones:")
    print(f"- Productos únicos: {df_inventario_aumentado['codigo_producto'].nunique()}")
    print(f"- Meses únicos: {df_inventario_aumentado['mes'].nunique()}")
    print(f"- Registros totales: {len(df_inventario_aumentado)}")
    
    # Distribución de alertas
    print("\n🚨 Distribución de alertas:")
    print(df_inventario_aumentado['alerta_stock'].value_counts())
    
    # Crear dataset final (sin la columna 'mes' para mantener formato original)
    df_final = df_inventario_aumentado.drop('mes', axis=1)
    
    # Guardar archivo aumentado
    output_file = 'data/dias_inventario_aumentado.csv'
    df_final.to_csv(output_file, index=False)
    print(f"\n💾 Archivo guardado: {output_file}")
    
    # Mostrar estadísticas finales
    print("\n📈 Estadísticas del dataset aumentado:")
    print(f"- Total de registros: {len(df_final)}")
    print(f"- Promedio de stock actual: {df_final['stock_actual'].mean():.2f}")
    print(f"- Promedio de días de inventario: {df_final['dias_inventario_disponible'].mean():.2f}")
    print(f"- Productos con stock crítico: {len(df_final[df_final['alerta_stock'] == 'CRÍTICO'])}")
    print(f"- Productos con exceso: {len(df_final[df_final['alerta_stock'] == 'EXCESO'])}")
    
    return df_final

if __name__ == "__main__":
    # Asegurarse de que estamos en el directorio correcto
    archivo_original = '../evaluacion_4/gold/original/recomendados_para_usar_por_profesor/dias_inventario.csv'
    
    if not os.path.exists(archivo_original):
        print(f"❌ Error: No se encuentra el archivo '{archivo_original}'")
        print("   Asegúrate de ejecutar este script desde el directorio sunmarket-dashboard/")
        exit(1)
    
    # Generar dataset aumentado
    df_aumentado = generar_dataset_aumentado()
    
    print("\n🎉 ¡Aumento de datos completado exitosamente!")
    print("\nPuedes usar el nuevo archivo 'dias_inventario_aumentado.csv' en tu análisis.")
