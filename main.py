import os
from scripts.data_loader import cargar_datos
# Ruta absoluta de la carpeta donde se encuentra el script (../scripts/)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Constuir la ruta del archivo csv de data

DATA_PATH = os.path.join(SCRIPT_DIR, '.', 'data', 'Hotel_Reviews.csv')

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