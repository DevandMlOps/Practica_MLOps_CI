import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import json

def load_and_validate_data(data_path):
    """Carga y valida los datos del dataset."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset no encontrado en: {data_path}")
    
    df = pd.read_csv(data_path)
    
    if df.empty:
        raise ValueError("El dataset está vacío")
    if 'diagnosis' not in df.columns:
        raise ValueError("Columna 'diagnosis' no encontrada")
    
    return df

def main():
    print("🧠 Iniciando entrenamiento del modelo...")
    
    # Carga y preparación de datos
    print("📊 Cargando datos...")
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'breast-cancer.csv')
    df = load_and_validate_data(data_path)
    
    print(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Limpieza básica
    df = df.drop(columns=['id', 'Unnamed: 32'], errors='ignore')
    df['diagnosis'] = df['diagnosis'].map({'M': 1, 'B': 0})
    
    # Validar que no hay valores nulos
    if df['diagnosis'].isnull().sum() > 0:
        raise ValueError("Valores nulos encontrados en diagnóstico")
    
    print(f"Distribución de clases:\n{df['diagnosis'].value_counts()}")
    
    # Separar features y target
    X = df.drop('diagnosis', axis=1)
    y = df['diagnosis']
    
    # División train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Conjunto de entrenamiento: {len(X_train)} muestras")
    print(f"Conjunto de prueba: {len(X_test)} muestras")
    
    # Normalización
    print("📏 Normalizando datos...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entrenamiento
    print("🎯 Entrenando modelo de Regresión Logística...")
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    # Evaluación
    print("📊 Evaluando modelo...")
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Precisión del modelo: {accuracy:.4f}")
    print("\n📋 Reporte detallado:")
    print(classification_report(y_test, y_pred, target_names=['Benigno', 'Maligno']))
    
    # Guardar artefactos
    print("💾 Guardando modelo y escalador...")
    output_dir = os.path.dirname(__file__)
    
    joblib.dump(model, os.path.join(output_dir, 'breast_cancer_model.joblib'))
    joblib.dump(scaler, os.path.join(output_dir, 'scaler.joblib'))
    
    # Guardar metadatos
    metadata = {
        'accuracy': float(accuracy),
        'feature_count': len(X.columns),
        'train_size': len(X_train),
        'test_size': len(X_test),
        'feature_names': list(X.columns)
    }
    
    with open(os.path.join(output_dir, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ Modelo entrenado y guardado exitosamente!")
    print(f"📁 Archivos creados en: {output_dir}/")

if __name__ == '__main__':
    main()
