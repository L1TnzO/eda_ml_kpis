import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

def generar_datos_temporales():
    """Genera datos temporales coherentes para inventario, ventas y transacciones"""
    
    # Cargar datos originales
    archivo_original = '../evaluacion_4/gold/original/recomendados_para_usar_por_profesor/dias_inventario.csv'
    df_original = pd.read_csv(archivo_original)
    print(f"✅ Datos originales cargados: {len(df_original)} productos")
    
    # Generar fechas diarias para 3 años (2022-2024)
    fecha_inicio = pd.to_datetime('2022-01-01')
    fecha_fin = pd.to_datetime('2024-12-31')
    fechas_diarias = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    
    print(f"📅 Generando datos para {len(fechas_diarias)} días: {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")
    
    # 1. Generar ventas diarias
    print("🔄 Generando ventas diarias...")
    ventas_diarias = []
    
    for fecha in fechas_diarias:
        # Simular ventas con variabilidad semanal y mensual
        base_ventas = 500000  # Ventas base diaria
        
        # Variabilidad por día de la semana (lunes más bajo, sábado más alto)
        dia_semana = fecha.weekday()
        multiplicador_semanal = [0.8, 0.9, 0.95, 1.0, 1.1, 1.3, 1.2][dia_semana]
        
        # Variabilidad por mes (diciembre más alto, febrero más bajo)
        mes = fecha.month
        multiplicador_mensual = [0.9, 0.8, 0.9, 1.0, 1.0, 1.0, 0.95, 0.95, 1.0, 1.1, 1.2, 1.4][mes-1]
        
        # Variabilidad aleatoria ±15%
        ruido = np.random.uniform(0.85, 1.15)
        
        ventas_dia = base_ventas * multiplicador_semanal * multiplicador_mensual * ruido
        
        ventas_diarias.append({
            'fecha': fecha,
            'ventas_totales_clp': round(ventas_dia, 0)
        })
    
    df_ventas = pd.DataFrame(ventas_diarias)
    
    # 2. Generar transacciones diarias
    print("🔄 Generando transacciones diarias...")
    transacciones_diarias = []
    
    for fecha in fechas_diarias:
        # Simular transacciones correlacionadas con ventas
        ventas_fecha = df_ventas[df_ventas['fecha'] == fecha]['ventas_totales_clp'].iloc[0]
        
        # Ticket promedio variable (entre 15000 y 35000)
        ticket_promedio = np.random.uniform(15000, 35000)
        
        # Calcular número de transacciones
        num_transacciones = int(ventas_fecha / ticket_promedio)
        
        # Agregar variabilidad ±10%
        num_transacciones = int(num_transacciones * np.random.uniform(0.9, 1.1))
        num_transacciones = max(10, num_transacciones)  # Mínimo 10 transacciones por día
        
        transacciones_diarias.append({
            'fecha': fecha,
            'numero_transacciones': num_transacciones
        })
    
    df_transacciones = pd.DataFrame(transacciones_diarias)
    
    # 3. Generar inventario temporal coherente
    print("🔄 Generando inventario temporal...")
    inventario_temporal = []
    
    # Para cada producto, generar datos temporales
    for idx, producto in df_original.iterrows():
        print(f"   Procesando producto {idx+1}/{len(df_original)}: {producto['descripcion']}")
        
        # Parámetros base del producto
        stock_inicial = producto['stock_actual']
        venta_base = producto['venta_promedio_diaria']
        dias_ventas_base = producto['dias_con_ventas']
        
        # Generar datos para fechas mensuales (para reducir tamaño)
        fechas_mensuales = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='MS')  # Primer día de cada mes
        
        stock_actual = stock_inicial
        
        for fecha_mes in fechas_mensuales:
            # Simular variabilidad en ventas (±30%)
            venta_simulada = venta_base * np.random.uniform(0.7, 1.3)
            
            # Simular variabilidad en días con ventas (±20%)
            dias_ventas = max(1, int(dias_ventas_base * np.random.uniform(0.8, 1.2)))
            
            # Calcular stock después de 30 días de ventas
            consumo_mensual = venta_simulada * 30
            stock_despues_ventas = max(0, stock_actual - consumo_mensual)
            
            # Calcular días de inventario
            if venta_simulada > 0:
                dias_inventario = stock_despues_ventas / venta_simulada
            else:
                dias_inventario = 999.0
            
            # Determinar alerta
            alerta = calcular_alerta(dias_inventario)
            
            # Reabastecer si es necesario (simulación realista)
            if alerta == 'CRÍTICO' or (alerta == 'BAJO' and np.random.random() < 0.6):
                # Reabastecer entre 30-90 días de inventario
                stock_reabastecido = venta_simulada * np.random.uniform(30, 90)
                stock_actual = stock_despues_ventas + stock_reabastecido
                dias_inventario = stock_actual / venta_simulada if venta_simulada > 0 else 999.0
                alerta = calcular_alerta(dias_inventario)
            else:
                stock_actual = stock_despues_ventas
            
            # Agregar registro
            inventario_temporal.append({
                'fecha_mes': fecha_mes,
                'codigo_producto': producto['codigo_producto'],
                'descripcion': producto['descripcion'],
                'stock_actual': round(stock_actual, 0),
                'dias_con_ventas': dias_ventas,
                'venta_promedio_diaria': round(venta_simulada, 2),
                'dias_inventario_disponible': round(dias_inventario, 2),
                'alerta_stock': alerta
            })
    
    df_inventario = pd.DataFrame(inventario_temporal)
    
    # 4. Guardar archivos
    print("💾 Guardando archivos...")
    
    # Asegurarse de que la carpeta data existe
    os.makedirs('data', exist_ok=True)
    
    # Guardar ventas diarias
    df_ventas.to_csv('data/ventas_diarias.csv', index=False)
    print(f"   ✅ Ventas diarias guardadas: {len(df_ventas)} registros")
    
    # Guardar transacciones diarias
    df_transacciones.to_csv('data/transacciones_diarias.csv', index=False)
    print(f"   ✅ Transacciones diarias guardadas: {len(df_transacciones)} registros")
    
    # Guardar inventario temporal (sin fecha para mantener formato original)
    df_inventario_final = df_inventario.drop('fecha_mes', axis=1)
    df_inventario_final.to_csv('data/dias_inventario_aumentado.csv', index=False)
    print(f"   ✅ Inventario temporal guardado: {len(df_inventario_final)} registros")
    
    # 5. Mostrar estadísticas finales
    print("\n📊 Estadísticas finales:")
    print(f"📈 Ventas diarias:")
    print(f"   - Total días: {len(df_ventas)}")
    print(f"   - Venta promedio: ${df_ventas['ventas_totales_clp'].mean():,.0f}")
    print(f"   - Venta máxima: ${df_ventas['ventas_totales_clp'].max():,.0f}")
    print(f"   - Venta mínima: ${df_ventas['ventas_totales_clp'].min():,.0f}")
    
    print(f"\n🛒 Transacciones diarias:")
    print(f"   - Total días: {len(df_transacciones)}")
    print(f"   - Transacciones promedio: {df_transacciones['numero_transacciones'].mean():.0f}")
    print(f"   - Transacciones máximas: {df_transacciones['numero_transacciones'].max()}")
    print(f"   - Transacciones mínimas: {df_transacciones['numero_transacciones'].min()}")
    
    print(f"\n📦 Inventario temporal:")
    print(f"   - Total registros: {len(df_inventario_final)}")
    print(f"   - Productos únicos: {df_inventario_final['codigo_producto'].nunique()}")
    print(f"   - Períodos por producto: {len(df_inventario_final) // df_inventario_final['codigo_producto'].nunique()}")
    print(f"   - Distribución de alertas:")
    print(df_inventario_final['alerta_stock'].value_counts().to_string())
    
    # 6. Verificar coherencia
    print("\n🔍 Verificación de coherencia:")
    
    # Calcular ticket promedio real
    ventas_total = df_ventas['ventas_totales_clp'].sum()
    transacciones_total = df_transacciones['numero_transacciones'].sum()
    ticket_promedio_real = ventas_total / transacciones_total if transacciones_total > 0 else 0
    
    print(f"   - Ticket promedio calculado: ${ticket_promedio_real:,.0f}")
    
    # Verificar que cada producto tiene datos temporales
    productos_inventario = df_inventario_final['codigo_producto'].nunique()
    productos_originales = df_original['codigo_producto'].nunique()
    
    print(f"   - Productos en inventario temporal: {productos_inventario}")
    print(f"   - Productos en datos originales: {productos_originales}")
    
    if productos_inventario == productos_originales:
        print("   ✅ Todos los productos tienen datos temporales")
    else:
        print("   ⚠️ Discrepancia en número de productos")
    
    return df_ventas, df_transacciones, df_inventario_final

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    archivo_original = '../evaluacion_4/gold/original/recomendados_para_usar_por_profesor/dias_inventario.csv'
    
    if not os.path.exists(archivo_original):
        print(f"❌ Error: No se encuentra el archivo '{archivo_original}'")
        print("   Asegúrate de ejecutar este script desde el directorio sunmarket-dashboard/")
        exit(1)
    
    print("🚀 Iniciando generación de datos temporales coherentes...")
    print("=" * 60)
    
    # Generar datos
    df_ventas, df_transacciones, df_inventario = generar_datos_temporales()
    
    print("\n" + "=" * 60)
    print("🎉 ¡Generación de datos completada exitosamente!")
    print("\nArchivos generados:")
    print("   📁 data/ventas_diarias.csv")
    print("   📁 data/transacciones_diarias.csv") 
    print("   📁 data/dias_inventario_aumentado.csv")
    print("\nEstos archivos son coherentes entre sí y listos para usar en el dashboard.")
