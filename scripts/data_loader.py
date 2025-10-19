import pandas as pd
import os

# Ruta absoluta de la carpeta donde se encuentra el script (../scripts/)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Constuir la ruta del archivo csv de data

DATA_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'Hotel_Reviews.csv')

# Creacion de funcion

def cargar_datos(path):
    print(f"Cargando datos desde: {path}")
    
    try:
        df = pd.read_csv(path)
        print("Datos cargados exitosamente.")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta especificada: {path}")
        print("Verifique que la ruta sea correcta y que el archivo exista.")
        return None
    except Exception as e:
        print(f"Ocurrió un error al cargar los datos: {e}")
        return None
    
    
# Este archivo se esta ejecutando directamente por el usuario o esta siendo importado por otro script

if __name__ == "__main__":
    # indica donde esta el script actualmente
    print(f"Ejecutando el script desde: {os.path.abspath(__file__)}")
    
    # Llamar a la funcion de arriba para cargar el csv
    dataframe_hotel_reviews = cargar_datos(DATA_PATH)
    
    if dataframe_hotel_reviews is not None:
        print("\n---Primeras 5 filas ---")
        print(dataframe_hotel_reviews.head())
        
        print("\n---Informacion del DataFrame ---")
        dataframe_hotel_reviews.info(show_counts=True)