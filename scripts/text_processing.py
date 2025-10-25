import re


def clean_text(text: str) -> str:
    
    # Limpia un texto eliminando valores por defecto y espacios excesivos.
    
    if not isinstance(text, str):
        return ""
    
    # Eliminar frases por defecto
    text = text.strip().replace("No Negative", "").replace("No Positive", "")
    
    # Normalizar espacios en blanco
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def compose_review(row) -> str:
    
    # Combina las reseñas positivas y negativas en un solo texto.
    
    positive = clean_text(row.get("Positive_Review", ""))
    negative = clean_text(row.get("Negative_Review", ""))
    
    combined = f"{positive}. {negative}".strip(". ")
    return combined


def clean_dataframe_reviews(df):
    
    # Limpia y combina las columnas de reseñas del DataFrame.
    
    df = df.copy()
    
    print("Limpiando texto de reseñas...")
    
    # Limpiar columnas individuales
    for col in ['Positive_Review', 'Negative_Review']:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Crear columna combinada
    print("Combinando reseñas positivas y negativas...")
    df['review_text'] = df.apply(compose_review, axis=1)
    
    return df
