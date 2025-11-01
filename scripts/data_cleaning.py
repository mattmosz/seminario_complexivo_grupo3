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


def get_country_mapping() -> dict:
    """
    Retorna un diccionario de mapeo para estandarizar nombres de países.
    
    Returns:
        Diccionario con variantes como claves y nombre estándar como valor
    """
    country_mapping = {
        # Reino Unido y variantes
        'United Kingdom': 'United Kingdom',
        'UK': 'United Kingdom',
        'Great Britain': 'United Kingdom',
        'England': 'United Kingdom',
        'Scotland': 'United Kingdom',
        'Wales': 'United Kingdom',
        'Northern Ireland': 'United Kingdom',
        'britain': 'United Kingdom',
        'uk': 'United Kingdom',
        'British Virgin Islands': 'United Kingdom',  # Territorio UK
        
        # Estados Unidos y variantes
        'United States of America': 'United States',
        'USA': 'United States',
        'US': 'United States',
        'United States': 'United States',
        'U.S.A.': 'United States',
        'U.S.': 'United States',
        'usa': 'United States',
        'us': 'United States',
        'American Samoa': 'United States',  # Territorio US
        'United States Minor Outlying Islands': 'United States',  # Territorio US
        
        # Países Bajos y variantes
        'Netherlands': 'Netherlands',
        'The Netherlands': 'Netherlands',
        'Holland': 'Netherlands',
        'nederland': 'Netherlands',
        
        # Corea
        'South Korea': 'South Korea',
        'Korea': 'South Korea',
        'Republic of Korea': 'South Korea',
        
        # Irlanda
        'Ireland': 'Ireland',
        'Republic of Ireland': 'Ireland',
        'Eire': 'Ireland',
        
        # Rusia
        'Russia': 'Russia',
        'Russian Federation': 'Russia',
        
        # Emiratos Árabes
        'United Arab Emirates': 'United Arab Emirates',
        'UAE': 'United Arab Emirates',
        'U.A.E.': 'United Arab Emirates',
        
        # China
        'China': 'China',
        'People\'s Republic of China': 'China',
        'PRC': 'China',
        
        # Hong Kong
        'Hong Kong': 'Hong Kong',
        'Hong Kong SAR': 'Hong Kong',
        
        # Taiwán
        'Taiwan': 'Taiwan',
        'Chinese Taipei': 'Taiwan',
        
        # República Checa
        'Czech Republic': 'Czech Republic',
        'Czechia': 'Czech Republic',
        
        # Otros casos comunes
        'New Zealand': 'New Zealand',
        'Saudi Arabia': 'Saudi Arabia',
        'South Africa': 'South Africa',
    }
    
    return country_mapping


def standardize_countries(df: pd.DataFrame, 
                         country_column: str = 'Reviewer_Nationality') -> pd.DataFrame:
    """
    Estandariza los nombres de países en la columna especificada.
    
    Args:
        df: DataFrame con columna de países
        country_column: Nombre de la columna con países
        
    Returns:
        DataFrame con países estandarizados
    """
    if country_column not in df.columns:
        print(f"Advertencia: Columna '{country_column}' no encontrada")
        return df
    
    df_clean = df.copy()
    
    print(f"Estandarizando nombres de países en '{country_column}'...")
    
    # Contar países únicos antes
    unique_before = df_clean[country_column].nunique()
    
    # PRIMERO: Limpiar espacios en blanco y normalizar
    df_clean[country_column] = df_clean[country_column].str.strip()
    
    # Obtener mapeo DESPUÉS de limpiar
    country_map = get_country_mapping()
    
    # Aplicar mapeo (case-insensitive)
    def map_country(country):
        if pd.isna(country) or country == '':
            return country
        
        # Buscar coincidencia exacta primero
        if country in country_map:
            return country_map[country]
        
        # Buscar coincidencia case-insensitive
        country_lower = country.lower()
        for key, value in country_map.items():
            if key.lower() == country_lower:
                return value
        
        # Si no hay mapeo, mantener el valor original capitalizado
        return country.strip()
    
    df_clean[country_column] = df_clean[country_column].apply(map_country)
    
    # Contar países únicos después
    unique_after = df_clean[country_column].nunique()
    
    print(f"   Países únicos antes: {unique_before}")
    print(f"   Países únicos después: {unique_after}")
    print(f"   Países consolidados: {unique_before - unique_after}")
    
    return df_clean
