import pandas as pd
from pathlib import Path


def load_dataset(file_path: str | Path, encoding: str = "utf-8") -> pd.DataFrame:
    
    # Carga el dataset de reseñas de hoteles.

    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"No se encuentra el archivo: {file_path}")
    
    print(f"Cargando datos desde: {file_path}")
    
    try:
        df = pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError:
        print("Error de codificación UTF-8, intentando con latin-1...")
        df = pd.read_csv(file_path, encoding="latin-1")
    
    print(f"Datos cargados: {df.shape[0]:,} filas, {df.shape[1]} columnas")
    return df


def get_sample(df: pd.DataFrame, n: int, random_state: int = 42) -> pd.DataFrame:
    
    # Obtiene una muestra aleatoria del DataFrame.
    
    sample_size = min(n, len(df))
    df_sample = df.sample(n=sample_size, random_state=random_state).reset_index(drop=True)
    print(f"Usando muestra de {sample_size:,} filas.")
    return df_sample


def save_processed_data(df: pd.DataFrame, 
                       output_path: str | Path,
                       encoding: str = "utf-8") -> None:
    
    # Guarda el DataFrame procesado en un archivo CSV.
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Guardando datos procesados en: {output_path}")
    df.to_csv(output_path, index=False, encoding=encoding)
    print(f"Archivo guardado exitosamente ({len(df):,} filas)")


def show_sentiment_distribution(df: pd.DataFrame, 
                                label_column: str = "sentiment_label") -> None:
    
    # Muestra la distribución de sentimientos en el DataFrame.
    
    if label_column not in df.columns:
        print(f"Columna '{label_column}' no encontrada en el DataFrame")
        return
    
    print("\n" + "="*50)
    print("DISTRIBUCIÓN DE SENTIMIENTOS")
    print("="*50)
    
    counts = df[label_column].value_counts(dropna=False)
    total = len(df)
    
    for label, count in counts.items():
        percentage = (count / total) * 100
        print(f"  {label:>10}: {count:>8,} ({percentage:>5.2f}%)")
    
    print("="*50 + "\n")


def get_data_summary(df: pd.DataFrame) -> None:
    
    # Muestra un resumen del DataFrame.
    
    print("\n" + "="*70)
    print("RESUMEN DEL DATASET")
    print("="*70)
    print(f"  Filas totales:     {len(df):>10,}")
    print(f"  Columnas totales:  {len(df.columns):>10}")
    print(f"  Memoria (MB):      {df.memory_usage(deep=True).sum() / 1024**2:>10.2f}")
    
    # Valores nulos
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print("\n  Columnas con valores nulos:")
        for col, count in null_counts[null_counts > 0].items():
            print(f"    - {col}: {count:,}")
    else:
        print("\n  No hay valores nulos")
    
    print("="*70 + "\n")


def prepare_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    
    # Prepara las columnas de salida del DataFrame procesado.
    
    # Columnas deseadas en orden
    cols_order = [
        "Hotel_Name", "Hotel_Address", "Reviewer_Nationality",
        "Positive_Review", "Negative_Review", "review_text",
        "compound", "pos", "neu", "neg", "sentiment_label",
        "Average_Score", "Reviewer_Score", "Tags", "lat", "lng"
    ]
    
    # Seleccionar solo las columnas que existen
    cols_available = [c for c in cols_order if c in df.columns]
    
    return df[cols_available].copy()
