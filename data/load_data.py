import pandas as pd
from sklearn.datasets import load_breast_cancer
import os

def create_breast_cancer_csv():
    """Crea el archivo CSV del dataset de cáncer de mama."""
    # Cargar datos de sklearn
    data = load_breast_cancer()
    
    # Crear DataFrame
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['diagnosis'] = ['M' if x == 1 else 'B' for x in data.target]
    
    # Agregar columna id (como en el dataset original)
    df.insert(0, 'id', range(len(df)))
    
    # Agregar columna vacía (como en el original)
    df['Unnamed: 32'] = None
    
    # Guardar CSV
    output_path = os.path.join(os.path.dirname(__file__), 'breast-cancer.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset guardado en: {output_path}")
    print(f"Forma del dataset: {df.shape}")
    print(f"Distribución diagnósticos:\n{df['diagnosis'].value_counts()}")

if __name__ == "__main__":
    create_breast_cancer_csv()
