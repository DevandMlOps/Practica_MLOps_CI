import os
import joblib
import numpy as np
import json
from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
from typing import List
from loguru import logger

# Configuración de la aplicación
app = Flask(__name__)

# Configurar logging
os.makedirs('logs', exist_ok=True)
logger.add("logs/api.log", rotation="10 MB", level="INFO")

# Variables globales
model = None
scaler = None
model_metadata = {}

def load_model_artifacts():
    """Carga el modelo, escalador y metadatos usando rutas absolutas."""
    global model, scaler, model_metadata
    
    # Obtener la ruta absoluta del directorio del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construir rutas absolutas a los artefactos
    MODEL_PATH = os.path.join(script_dir, '..', 'model', 'breast_cancer_model.joblib')
    SCALER_PATH = os.path.join(script_dir, '..', 'model', 'scaler.joblib')
    METADATA_PATH = os.path.join(script_dir, '..', 'model', 'model_metadata.json')
    
    try:
        # Cargar modelo
        model = joblib.load(MODEL_PATH)
        logger.info(f"Modelo cargado desde: {MODEL_PATH}")
        
        # Cargar escalador
        scaler = joblib.load(SCALER_PATH)
        logger.info(f"Escalador cargado desde: {SCALER_PATH}")
        
        # Cargar metadatos si existen
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r') as f:
                model_metadata = json.load(f)
            logger.info(f"Metadatos cargados desde: {METADATA_PATH}")
        
        logger.info(f"Modelo cargado exitosamente. Precisión: {model_metadata.get('accuracy', 'N/A')}")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"Archivo del modelo no encontrado: {e}")
        return False
    except Exception as e:
        logger.error(f"Error cargando artefactos del modelo: {e}")
        return False

# Cargar modelo al inicializar
model_loaded = load_model_artifacts()

# Validación con Pydantic
class PredictionInput(BaseModel):
    features: List[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 
                           0.3001, 0.1471, 0.2419, 0.07871, 1.095, 0.9053, 
                           8.589, 153.4, 0.006399, 0.04904, 0.05373, 0.01587, 
                           0.03003, 0.006193, 25.38, 17.33, 184.6, 2019.0, 
                           0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189]
            }
        }

    def validate_features(self):
        """Validación adicional."""
        expected_count = model_metadata.get('feature_count', 30)
        if len(self.features) != expected_count:
            raise ValueError(f"Se esperaban {expected_count} features, recibidas {len(self.features)}")
        
        features_array = np.array(self.features)
        if np.any(np.isnan(features_array)) or np.any(np.isinf(features_array)):
            raise ValueError("Features contienen valores inválidos")

    def to_numpy(self):
        return np.array(self.features).reshape(1, -1)

# Rutas de la API
@app.route('/', methods=['GET'])
def health_check():
    """Endpoint de estado."""
    status = {
        "status": "ok" if model_loaded else "degraded",
        "message": "API de diagnóstico de cáncer de mama",
        "model_loaded": model_loaded,
        "model_accuracy": model_metadata.get('accuracy', 'N/A')
    }
    logger.info("Health check solicitado")
    return jsonify(status), 200 if model_loaded else 503

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint de predicción."""
    if not model_loaded:
        logger.error("Intento de predicción sin modelo")
        return jsonify({"error": "Modelo no disponible"}), 503

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No se proporcionaron datos JSON"}), 400

    try:
        # Validación
        input_data = PredictionInput(**json_data)
        input_data.validate_features()

        # Predicción
        data_to_predict = input_data.to_numpy()
        data_scaled = scaler.transform(data_to_predict)
        
        prediction = model.predict(data_scaled)
        prediction_proba = model.predict_proba(data_scaled)

        result = {
            "prediction": "Maligno" if int(prediction[0]) == 1 else "Benigno",
            "confidence": {
                "Benigno": round(float(prediction_proba[0][0]), 4),
                "Maligno": round(float(prediction_proba[0][1]), 4)
            },
            "prediction_numeric": int(prediction[0])
        }
        
        logger.info(f"Predicción: {result['prediction']}")
        return jsonify(result), 200

    except ValidationError as e:
        logger.warning(f"Error de validación: {e.errors()}")
        return jsonify({"error": "Datos inválidos", "details": e.errors()}), 422
    except ValueError as e:
        logger.warning(f"Error en datos: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
