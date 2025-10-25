import argparse
from pathlib import Path

# Importar módulos del proyecto
from scripts.data_processing import (
    load_dataset, 
    get_sample, 
    save_processed_data,
    show_sentiment_distribution,
    get_data_summary
)
from scripts.data_cleaning import (
    clean_and_compose_reviews,
    remove_duplicates,
    handle_missing_values,
    validate_data_types
)
from scripts.text_processing import clean_dataframe_reviews
from scripts.sentiment_analysis import sentiment_chunked
from scripts.topic_modeling import extract_topics, print_topics


# Configuración de rutas
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_IN = DATA_DIR / "Hotel_Reviews.csv"
DATA_OUT = DATA_DIR / "hotel_reviews_processed.csv"


def parse_arguments():
    
    # Parsea los argumentos de línea de comandos.
    
    parser = argparse.ArgumentParser(
        description="Pipeline de análisis de sentimientos para reseñas de hoteles"
    )
    
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Usar muestra aleatoria de N filas (0 = usar todas)"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100_000,
        help="Tamaño de bloque para procesamiento de sentimientos"
    )
    
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Escribir resultados incrementalmente (menor uso de RAM)"
    )
    
    parser.add_argument(
        "--topics",
        action="store_true",
        help="Ejecutar modelado de tópicos con LDA"
    )
    
    parser.add_argument(
        "--n-topics",
        type=int,
        default=8,
        help="Número de tópicos a extraer"
    )
    
    parser.add_argument(
        "--skip-sentiment",
        action="store_true",
        help="Saltar análisis de sentimientos (solo limpieza)"
    )
    
    return parser.parse_args()


def main():
    
    # Función principal que ejecuta el pipeline completo.
    
    args = parse_arguments()
    
    print("\n" + "="*70)
    print("ANÁLISIS DE SENTIMIENTOS - RESEÑAS DE HOTELES")
    print("="*70 + "\n")
    
    # CARGA DE DATOS
    print("FASE 1: CARGA DE DATOS")
    print("-" * 70)
    
    df = load_dataset(DATA_IN)
    
    # Usar muestra si se especifica
    if args.sample > 0:
        df = get_sample(df, args.sample)
    
    get_data_summary(df)
    
    # LIMPIEZA DE DATOS
    print("FASE 2: LIMPIEZA DE DATOS")
    print("-" * 70)
    
    # Validar tipos de datos
    df = validate_data_types(df)
    
    # Manejar valores faltantes
    df = handle_missing_values(df)
    
    # Eliminar duplicados
    df = remove_duplicates(df)
    
    # Limpiar y combinar reseñas
    df = clean_and_compose_reviews(df)
    
    # Procesar texto (crear columna review_text)
    df = clean_dataframe_reviews(df)
    
    print()
    
    # ANÁLISIS DE SENTIMIENTOS
    if not args.skip_sentiment:
        print("FASE 3: ANÁLISIS DE SENTIMIENTOS")
        print("-" * 70)
        
        if args.stream:
            # Modo streaming: escribe directamente al archivo
            if DATA_OUT.exists():
                DATA_OUT.unlink()
            
            sentiment_chunked(df, chunk_size=args.chunk_size, stream_path=DATA_OUT)
            print(f"Resultados guardados (streaming) en: {DATA_OUT}\n")
            
            # Cargar para análisis adicional si es necesario
            if args.topics:
                df_processed = load_dataset(DATA_OUT)
            else:
                df_processed = None
        else:
            # Modo en memoria: procesa todo y guarda al final
            df_processed = sentiment_chunked(df, chunk_size=args.chunk_size, stream_path=None)
            
            # Mostrar distribución de sentimientos
            show_sentiment_distribution(df_processed)
            
            # Guardar resultados
            save_processed_data(df_processed, DATA_OUT)
            print()
    else:
        print("FASE 3: ANÁLISIS DE SENTIMIENTOS (OMITIDO)")
        print("-" * 70)
        df_processed = df
        
        # Guardar datos limpios aunque se omita el análisis de sentimientos
        save_processed_data(df_processed, DATA_OUT)
        print()
    
    # FASE 4: MODELADO DE TÓPICOS
    if args.topics:
        print("FASE 4: MODELADO DE TÓPICOS")
        print("-" * 70)
        
        # Usar datos procesados si están disponibles
        df_for_topics = df_processed if df_processed is not None else df
        
        # Asegurar que existe la columna de texto
        if "review_text" not in df_for_topics.columns:
            print("No se encuentra columna 'review_text'. Creándola...")
            df_for_topics = clean_dataframe_reviews(df_for_topics)
        
        # Extraer tópicos
        topics = extract_topics(
            df_for_topics,
            n_topics=args.n_topics,
            text_column="review_text"
        )
        
        # Mostrar resultados
        print_topics(topics)
    
    # RESUMEN FINAL
    print("="*70)
    print("PIPELINE COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"Archivo de salida: {DATA_OUT}")
    print(f"Registros procesados: {len(df):,}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
