import re
import unicodedata
import pandas as pd

# ============================================================
# 0) Utilidades para normalizar países (ISO-like, estricto)
# ============================================================

# Lista de ~195 países (nombres cortos comunes en inglés)
VALID_COUNTRIES = {
    "Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia",
    "Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin",
    "Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi",
    "Cabo Verde","Cambodia","Cameroon","Canada","Central African Republic","Chad","Chile","China","Colombia","Comoros",
    "Congo","Democratic Republic of the Congo","Costa Rica","Cote d'Ivoire","Croatia","Cuba","Cyprus","Czechia",
    "Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea",
    "Estonia","Eswatini","Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece",
    "Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Indonesia",
    "Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kuwait",
    "Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg",
    "Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico",
    "Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal",
    "Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","North Macedonia","Norway","Oman","Pakistan",
    "Palau","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia",
    "Rwanda","Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino",
    "Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia",
    "Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan",
    "Suriname","Sweden","Switzerland","Syria","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga",
    "Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates",
    "United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Yemen",
    "Zambia","Zimbabwe"
}

# Territorios / subnacionales / alias → país
TERRITORY_TO_COUNTRY = {
    # US & UK & NL & FR territories + subnacionales frecuentes
    "usa":"United States","u.s.a":"United States","us":"United States","america":"United States",
    "puerto rico":"United States","guam":"United States","american samoa":"United States",
    "us virgin islands":"United States","united states of america":"United States",
    "england":"United Kingdom","scotland":"United Kingdom","wales":"United Kingdom",
    "northern ireland":"United Kingdom","uk":"United Kingdom","u.k.":"United Kingdom","great britain":"United Kingdom",
    "britain":"United Kingdom","gibraltar":"United Kingdom","isle of man":"United Kingdom","jersey":"United Kingdom","guernsey":"United Kingdom",
    "holland":"Netherlands","the netherlands":"Netherlands","curaçao":"Netherlands","curacao":"Netherlands",
    "bonaire":"Netherlands","sint maarten":"Netherlands","aruba":"Netherlands",
    "reunion":"France","réunion":"France","martinique":"France","guadeloupe":"France","mayotte":"France",
    "new caledonia":"France","french polynesia":"France","saint martin":"France","st martin":"France","saint barthelemy":"France",
    "faroe islands":"Denmark","greenland":"Denmark",
    # China / SAR
    "hong kong":"China","hong kong sar":"China","macau":"China","macao":"China","people's republic of china":"China","prc":"China",
    # Korea
    "republic of korea":"South Korea","korea, republic of":"South Korea","south korea":"South Korea","korea":"South Korea",
    "democratic people's republic of korea":"North Korea","dprk":"North Korea","north korea":"North Korea",
    # Czechia / others
    "czech republic":"Czechia","russian federation":"Russia","viet nam":"Vietnam","uae":"United Arab Emirates","u.a.e.":"United Arab Emirates",
    "iran, islamic republic of":"Iran","syrian arab republic":"Syria","tanzania, united republic of":"Tanzania",
    "lao people's democratic republic":"Laos","moldova, republic of":"Moldova","bolivia, plurinational state of":"Bolivia",
    "venezuela, bolivarian republic of":"Venezuela","brunei darussalam":"Brunei",
    # Congo variants
    "dr congo":"Democratic Republic of the Congo","congo (kinshasa)":"Democratic Republic of the Congo",
    "democratic republic of congo":"Democratic Republic of the Congo",
    "congo (brazzaville)":"Congo","republic of the congo":"Congo",
    # Ivory Coast
    "cote d’ivoire":"Cote d'Ivoire","côte d’ivoire":"Cote d'Ivoire","cote d'ivoire":"Cote d'Ivoire","côte d'ivoire":"Cote d'Ivoire",
    # Otros comunes
    "myanmar (burma)":"Myanmar","eswatini (swaziland)":"Eswatini","swaziland":"Eswatini",
    "cape verde":"Cabo Verde","east timor":"Timor-Leste","burma":"Myanmar",
    # No-país / región / basura → None (filtrar)
    "europe": None, "european union": None, "schengen": None, "other": None, "unknown": None,
    "nan": None, "-": None, "—": None
}

def _slug(s: str) -> str:
    """Minúsculas, sin acentos, solo letras/espacios, colapsa espacios."""
    s = s or ""
    s = s.strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.lower()
    s = re.sub(r"[^a-z' ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def canonical_country(raw: str):
    """
    Normaliza 'nacionalidad/país' a un país ISO corto (VALID_COUNTRIES).
    Retorna None si no es un país (región/otro/lixo).
    """
    if not isinstance(raw, str) or not raw.strip():
        return None
    s = _slug(raw)

    # 1) Mapeo directo de territorios/alias
    if s in TERRITORY_TO_COUNTRY:
        return TERRITORY_TO_COUNTRY[s]

    # 2) Heurísticas de frases tipo 'republic of ...'
    s2 = (
        s.replace("islamic republic of ", "")
         .replace("republic of ", "")
         .replace("federative republic of ", "")
         .replace("federation of ", "")
         .replace("state of ", "")
         .replace("plurinational state of ", "")
         .replace("kingdom of ", "")
         .replace("the ", "")
         .strip()
    )

    # 3) Coincidencia exacta en lista válida (title-case)
    tc = re.sub(r"\s+", " ", s2).title()
    if tc in VALID_COUNTRIES:
        return tc

    # 4) Split por coma/paréntesis/and (e.g., 'Congo (Kinshasa)')
    s3 = re.split(r"[,(]|\band\b", s2)[0].strip()
    tc3 = s3.title()
    if tc3 in VALID_COUNTRIES:
        return tc3

    # 5) Reglas específicas tardías
    if s in {"kosovo","xk","xkx"}:
        # Estricto ISO: descartar (no ISO 3166-1 oficial)
        return None
    if s in {"eng","gb","gbr"}:
        return "United Kingdom"
    if s in {"usa","us","usa "}:
        return "United States"

    # 6) Nada encaja → None (se filtra)
    return None

def standardize_countries_strict(df: pd.DataFrame, col: str = "Reviewer_Nationality") -> pd.DataFrame:
    """
    Normaliza países con reglas estrictas (ISO-like) + filtra no-países.
    """
    if col not in df.columns:
        print(f"[WARN] Columna '{col}' no existe; skip.")
        return df
    print("Normalizando países (estricto ISO + territorios → país)…")
    before = df[col].nunique(dropna=True)
    df = df.copy()
    df[col] = df[col].apply(canonical_country)
    df = df[~df[col].isna()].reset_index(drop=True)  # filtra None
    after = df[col].nunique(dropna=True)
    print(f"   Únicos antes: {before} → después: {after} (consolidados: {before - after})")
    return df

# ============================================================
# 1) Limpieza de texto (tus funciones originales (Matías Mosquera))
# ============================================================

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


def standardize_countries(df: pd.DataFrame, country_column: str = 'Reviewer_Nationality',
                          strict: bool = True) -> pd.DataFrame:
    """
    API de compatibilidad:
      - strict=True  -> usa el normalizador ISO-like (recomendado)
      - strict=False -> usa el mapeo básico legacy (tu función original)
    """
    if not strict:
        # ---- Legacy: implementación original (Matías Mosquera), con mejoras mínimas(FQ)----
        if country_column not in df.columns:
            print(f"Advertencia: Columna '{country_column}' no encontrada")
            return df
        df_clean = df.copy()
        print(f"Estandarizando nombres de países en '{country_column}' (LEGACY)...")
        unique_before = df_clean[country_column].nunique()
        df_clean[country_column] = df_clean[country_column].astype(str).str.strip()

        country_map = get_country_mapping()

        def map_country(country):
            if pd.isna(country) or country == '':
                return country
            if country in country_map:
                return country_map[country]
            country_lower = country.lower()
            for key, value in country_map.items():
                if key.lower() == country_lower:
                    return value
            return country.strip()

        df_clean[country_column] = df_clean[country_column].apply(map_country)
        unique_after = df_clean[country_column].nunique()
        print(f"   Países únicos antes: {unique_before}")
        print(f"   Países únicos después: {unique_after}")
        print(f"   Países consolidados: {unique_before - unique_after}")
        return df_clean
    

    # ---- Estricto (recomendado) ----
    return standardize_countries_strict(df, col=country_column)

def country_consolidation_report(df: pd.DataFrame, col: str = "Reviewer_Nationality") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Devuelve:
      - consolidated: por país canónico -> total filas, #alias, lista de alias
      - dropped: valores originales que fueron descartados (None) con sus conteos
    """
    if col not in df.columns:
        raise KeyError(f"Columna '{col}' no existe en el DataFrame.")

    tmp = df[[col]].copy()
    tmp["__original__"] = tmp[col].astype(str)
    tmp["__canonical__"] = tmp["__original__"].apply(canonical_country)

    # Alias que sí consolidaron en un país válido
    kept = tmp[~tmp["__canonical__"].isna()].copy()
    alias_counts = kept.groupby(["__canonical__", "__original__"]).size().reset_index(name="rows")

    # Resumen por país canónico
    consolidated = (
        alias_counts.groupby("__canonical__")
        .agg(
            total_rows=("rows", "sum"),
            alias_count=("__original__", "nunique"),
            aliases=("__original__", lambda s: sorted(s.unique()))
        )
        .reset_index()
        .rename(columns={"__canonical__": "country"})
        .sort_values(["alias_count", "total_rows"], ascending=[False, False])
    )

    # Valores descartados (no-país/ruido)
    dropped = (
        tmp[tmp["__canonical__"].isna()]
        .groupby("__original__")
        .size()
        .reset_index(name="rows")
        .sort_values("rows", ascending=False)
        .rename(columns={"__original__": "dropped_value"})
    )

    return consolidated, dropped

# ============================================================
# 4) Pipeline helper (opcional)
# ============================================================

def apply_full_cleaning(df: pd.DataFrame,
                        country_col: str = "Reviewer_Nationality",
                        strict_countries: bool = True) -> pd.DataFrame:
    """
    Pipeline recomendado: tipos → nulos → duplicados → reseñas → países (estricto).
    """
    df = validate_data_types(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = clean_and_compose_reviews(df)
    df = standardize_countries(df, country_column=country_col, strict=strict_countries)
    return df