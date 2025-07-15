import pandas as pd
import streamlit as st

@st.cache_data
def load_inventory_data(use_augmented=False):
    """Cargar datos de inventario - original o aumentado"""
    if use_augmented:
        try:
            df = pd.read_csv('data/dias_inventario_aumentado.csv')
            return df
        except FileNotFoundError:
            st.warning("⚠️ Archivo aumentado no encontrado, usando datos originales")
            return pd.read_csv('data/dias_inventario.csv')
    else:
        return pd.read_csv('data/dias_inventario.csv')

@st.cache_data
def load_sales_data():
    """Cargar datos de ventas diarias"""
    df = pd.read_csv('data/ventas_diarias.csv')
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

@st.cache_data
def load_transactions_data():
    """Cargar datos de transacciones diarias"""
    df = pd.read_csv('data/transacciones_diarias.csv')
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

@st.cache_data
def load_all_data(use_augmented=False):
    """Cargar todos los datos principales"""
    inventory = load_inventory_data(use_augmented)
    sales = load_sales_data()
    transactions = load_transactions_data()
    return inventory, sales, transactions

def get_data_info(use_augmented=False):
    """Obtener información sobre el dataset seleccionado"""
    inventory = load_inventory_data(use_augmented)
    
    if use_augmented:
        return {
            'tipo': 'Dataset Aumentado',
            'descripcion': 'Datos históricos simulados (2022-2024)',
            'registros': len(inventory),
            'productos': inventory['codigo_producto'].nunique(),
            'periodo': '36 meses de datos sintéticos'
        }
    else:
        return {
            'tipo': 'Dataset Original',
            'descripcion': 'Datos originales de la capa gold',
            'registros': len(inventory),
            'productos': inventory['codigo_producto'].nunique(),
            'periodo': 'Snapshot actual'
        }
