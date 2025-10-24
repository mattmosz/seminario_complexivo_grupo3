import pandas as pd

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

