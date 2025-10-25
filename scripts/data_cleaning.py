# scripts/data_cleaning.py
"""
Módulo para limpieza y preparación de datos del dataset de reseñas.
"""
import re
import pandas as pd


def clean_text(text: str) -> str:
    """
    Limpia un texto individual eliminando valores por defecto y normalizando espacios.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        Texto limpio
    """
    if not isinstance(text, str):
        return ""
    
    # Eliminar frases por defecto
    text = text.strip().replace("No Negative", "").replace("No Positive", "")
    
    # Normalizar espacios en blanco
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def clean_and_compose_reviews(df):
    """
    Limpia y combina las columnas Positive_Review y Negative_Review del dataframe.
    
    Args:
        df: DataFrame con columnas de reseñas
        
    Returns:
        DataFrame con columnas limpias y Combined_Review
    """
    df = df.copy()
    
    # Limpiar columnas
    print("Iniciando limpieza de texto en las reseñas...")
    for col in ['Positive_Review', 'Negative_Review']:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Combinar reseñas
    print("Combinando reseñas positivas y negativas para crear 'Combined_Review'...")
    df['Combined_Review'] = df.apply(
        lambda row: f"{row['Positive_Review']}. {row['Negative_Review']}".strip(". "),
        axis=1
    )
    
    print("Limpieza completada")
    return df


def remove_duplicates(df: pd.DataFrame, subset=None) -> pd.DataFrame:
    """
    Elimina filas duplicadas del DataFrame.
    
    Args:
        df: DataFrame original
        subset: Lista de columnas para considerar duplicados (None = todas)
        
    Returns:
        DataFrame sin duplicados
    """
    original_count = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep='first').reset_index(drop=True)
    removed = original_count - len(df_clean)
    
    if removed > 0:
        print(f"Eliminados {removed:,} registros duplicados")
    else:
        print("No se encontraron duplicados")
    
    return df_clean


def handle_missing_values(df: pd.DataFrame, strategy: dict = None) -> pd.DataFrame:
    """
    Maneja valores faltantes según estrategia especificada.
    
    Args:
        df: DataFrame original
        strategy: Diccionario con estrategias por columna
                 Ej: {'columna': 'drop', 'otra': 'fill', 'valor': 0}
        
    Returns:
        DataFrame con valores faltantes manejados
    """
    df_clean = df.copy()
    
    # Contar valores nulos iniciales
    null_counts = df_clean.isnull().sum()
    has_nulls = null_counts[null_counts > 0]
    
    if len(has_nulls) == 0:
        print("No hay valores faltantes")
        return df_clean
    
    print("Valores faltantes encontrados:")
    for col, count in has_nulls.items():
        print(f"   - {col}: {count:,}")
    
    # Aplicar estrategia por defecto si no se especifica
    if strategy is None:
        # Rellenar con valores por defecto según tipo
        for col in has_nulls.index:
            if df_clean[col].dtype in ['float64', 'int64']:
                df_clean[col].fillna(0, inplace=True)
            else:
                df_clean[col].fillna("", inplace=True)
        print("Valores faltantes rellenados con valores por defecto")
    
    return df_clean


def validate_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida y convierte tipos de datos según sea necesario.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        DataFrame con tipos de datos validados
    """
    df_clean = df.copy()
    
    print("Validando tipos de datos...")
    
    # Asegurar que las columnas de texto sean string
    text_cols = ['Hotel_Name', 'Hotel_Address', 'Reviewer_Nationality', 
                 'Positive_Review', 'Negative_Review']
    
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str)
    
    # Asegurar que las columnas numéricas sean numeric
    numeric_cols = ['Average_Score', 'Reviewer_Score']
    
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    print("Tipos de datos validados")
    return df_clean


