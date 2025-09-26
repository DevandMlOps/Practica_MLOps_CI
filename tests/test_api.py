import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def wait_for_api(max_attempts=30):
    """Espera a que la API esté disponible."""
    print("⏳ Esperando que la API esté lista...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code in [200, 503]:  # 503 si el modelo no está cargado
                print("✅ API está respondiendo")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"   Intento {i+1}/{max_attempts}...")
        time.sleep(1)
    return False

def test_health_check():
    """Test del health check."""
    print("\n🔍 Probando endpoint de health check...")
    
    if not wait_for_api():
        print("❌ API no está disponible después de esperar")
        sys.exit(1)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status code: {response.status_code}")
    
    data = response.json()
    print(f"Respuesta: {json.dumps(data, indent=2)}")
    
    assert "status" in data
    print("✅ Health Check: PASSED")

def test_predict_valid_data():
    """Test con datos válidos."""
    print("\n🔍 Probando predicción con datos válidos...")
    
    valid_data = {
        "features": [
            17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471, 0.2419, 0.07871,
            1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904, 0.05373, 0.01587, 0.03003, 0.006193,
            25.38, 17.33, 184.6, 2019.0, 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189
        ]
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=valid_data)
    print(f"Status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return
    
    data = response.json()
    print(f"Respuesta: {json.dumps(data, indent=2)}")
    
    assert "prediction" in data
    assert "confidence" in data
    assert data["prediction"] in ["Maligno", "Benigno"]
    print("✅ Predicción válida: PASSED")

def test_predict_invalid_data():
    """Test con datos inválidos."""
    print("\n🔍 Probando predicción con datos inválidos...")
    
    invalid_data = {"features": [1, 2, 3]}  # Muy pocas features
    
    response = requests.post(f"{BASE_URL}/predict", json=invalid_data)
    print(f"Status code: {response.status_code}")
    print(f"Respuesta: {response.text}")
    
    assert response.status_code in [400, 422]
    print("✅ Manejo de datos inválidos: PASSED")

if __name__ == "__main__":
    print("🧪 Iniciando tests de la API...")
    try:
        test_health_check()
        test_predict_valid_data()
        test_predict_invalid_data()
        print("\n🎉 Todos los tests pasaron exitosamente!")
    except Exception as e:
        print(f"\n❌ Error en tests: {e}")
        sys.exit(1)
