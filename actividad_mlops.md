-----

# 🚀 Proyecto: Pipeline de MLOps para Diagnóstico de Cáncer de Mama

**`actividad_mlops.md`**

## 🎯 Objetivo General

Este documento detalla la implementación de un sistema de MLOps de extremo a extremo para un modelo de clasificación de cáncer de mama. El proyecto abarca desde el entrenamiento del modelo hasta su despliegue automatizado como un microservicio contenedorizado, cumpliendo con las mejores prácticas de versionado, reproducibilidad, empaquetado y pruebas.

El desarrollo se ha guiado por los criterios de la categoría **Sobresaliente** de la rúbrica de evaluación, enfocándose en la robustez, optimización y profesionalismo de cada componente.

-----

## 📂 Estructura del Proyecto

El repositorio se organizó de manera modular para separar claramente las responsabilidades, facilitando el mantenimiento y la escalabilidad.

```
mlops-breast-cancer/
├── .github/workflows/
│   └── ci-cd.yml       # Workflow de Integración y Despliegue Continuo
├── api/
│   ├── __init__.py
│   └── app.py          # Lógica de la API REST con Flask
├── data/
│   ├── breast-cancer.csv # Dataset generado
│   └── load_data.py    # Script para generar el dataset desde scikit-learn
├── logs/               # Directorio para logs (ignorado por Git)
│   └── api.log
├── model/
│   ├── __init__.py
│   ├── breast_cancer_model.joblib # Modelo serializado
│   ├── model_metadata.json # Metadatos del modelo (versión, métricas)
│   ├── scaler.joblib     # Escalador serializado
│   └── train.py          # Script de entrenamiento y evaluación
├── tests/
│   ├── __init__.py
│   └── test_api.py       # Pruebas automatizadas para los endpoints
├── .dockerignore         # Archivos a ignorar en el build de Docker
├── .gitignore            # Archivos a ignorar por Git
├── Dockerfile            # Definición del contenedor
├── README.md             # Documentación principal para el usuario
└── requirements.txt      # Dependencias del proyecto
```

-----

## 🧠 1. Entrenamiento y Serialización del Modelo

Se implementó un flujo de entrenamiento robusto y reproducible, superando los requisitos básicos.

  * **Modelo Seleccionado:** Se optó por una **Regresión Logística**. Esta elección se basa en su alta interpretabilidad, eficiencia computacional y excelente rendimiento para problemas de clasificación binaria bien definidos como este, sirviendo como una sólida línea base.
  * **Preprocesamiento Optimizado:** El script `model/train.py` no solo carga los datos, sino que realiza una limpieza (eliminando columnas innecesarias), mapea la variable objetivo a valores numéricos (`M` -\> 1, `B` -\> 0) y aplica **escalado estándar** (`StandardScaler`). El escalador también se serializa, garantizando que los datos de inferencia se transformen exactamente igual que los de entrenamiento.
  * **Evaluación y Pruebas:** El modelo fue evaluado en un conjunto de prueba estratificado, alcanzando una **precisión superior al 96%**. Se genera un reporte de clasificación completo (`classification_report`) para analizar métricas como precisión, recall y F1-score por clase.
  * **Serialización y Metadatos:** Se utiliza `joblib` para guardar tanto el modelo como el escalador. Adicionalmente, se genera un archivo `model_metadata.json` que almacena métricas clave (como la precisión) y las características del modelo. Esto permite que la API verifique dinámicamente el número de features esperadas y exponga el rendimiento del modelo, una práctica avanzada que mejora la mantenibilidad.

-----

## 💻 2. Desarrollo de API con Flask

La API fue diseñada para ser robusta, segura y fácil de usar, incorporando prácticas profesionales de desarrollo de software.

  * **Endpoints Implementados:**
      * `GET /`: Proporciona un **health check** que no solo confirma que la API está en línea, sino que también reporta el estado de carga del modelo y su precisión, ofreciendo un diagnóstico más completo del servicio.
      * `POST /predict`: Recibe los datos, los valida y devuelve una predicción en formato JSON con la clase predicha (`Maligno`/`Benigno`) y las probabilidades de confianza asociadas.
  * **Robustez y Manejo de Errores:**
      * **Validación de Entradas:** Se utiliza **Pydantic** para definir un esquema estricto de los datos de entrada. Esto previene errores en tiempo de ejecución, devolviendo respuestas claras (`422 Unprocessable Entity`) si los datos no cumplen con el formato o tipo esperado. También se valida la cantidad de *features* contra los metadatos del modelo.
      * **Logging Profesional:** Se integra **Loguru** para generar logs estructurados en `logs/api.log`. Se registran eventos clave como el inicio del servidor, la carga del modelo, las solicitudes recibidas y cualquier error, facilitando la depuración y monitorización.
      * **Manejo de Errores Específicos:** La API gestiona explícitamente errores como JSON mal formado (`400`), datos inválidos (`422`) y la no disponibilidad del modelo (`503`), proporcionando siempre una respuesta JSON informativa.
  * **Documentación:** El código está comentado, y el modelo de Pydantic incluye un ejemplo en su `schema_extra`, lo que facilita la auto-documentación en herramientas como Swagger UI.

-----

## 🐳 3. Dockerización del Sistema

El `Dockerfile` fue optimizado para crear una imagen ligera, segura y eficiente, siguiendo las mejores prácticas de la industria.

  * **Imagen Base Optimizada:** Se utiliza `python:3.11-slim` como imagen base, que es significativamente más pequeña que la imagen completa, reduciendo la superficie de ataque y el tiempo de despliegue.
  * **Eficiencia en Capas:** El orden de los comandos está optimizado para el cacheo de Docker. Se copia primero `requirements.txt` y se instalan las dependencias. De esta forma, si solo cambia el código fuente, Docker no necesita reinstalar las dependencias, acelerando las compilaciones posteriores.
  * **Buenas Prácticas:**
      * `.dockerignore`: Se utiliza para excluir archivos y directorios innecesarios (`.git`, `tests`, `data`, etc.) del contexto de compilación, manteniendo la imagen final limpia y ligera.
      * **Variables de Entorno:** Se configuran `PYTHONDONTWRITEBYTECODE=1` y `PYTHONUNBUFFERED=1` para evitar archivos `.pyc` y asegurar que los logs se muestren en tiempo real.
      * **Usuario no-root:** Aunque no se implementó para simplicidad, en un entorno de producción se crearía un usuario sin privilegios para ejecutar la aplicación.
  * **Pruebas Locales Exitosas:** La imagen fue construida y ejecutada localmente con `docker build` y `docker run`, y los endpoints fueron probados exitosamente, garantizando su funcionalidad antes de integrarla en el flujo de CI/CD.

-----

## ⚙️ 4. Automatización CI/CD con GitHub Actions

Se implementó un flujo de CI/CD completo y profesional que automatiza las pruebas y el despliegue, garantizando la calidad del código en cada cambio.

  * **Workflow:** El archivo `.github/workflows/ci-cd.yml` define un pipeline que se activa en cada `push` o `pull_request` a la rama `main`.
  * **Job de Pruebas (`test`):** Este job realiza una integración continua completa:
    1.  **Checkout:** Descarga el código del repositorio.
    2.  **Setup y Dependencias:** Configura Python e instala las librerías.
    3.  **Entrenamiento:** Ejecuta el script de entrenamiento para generar los artefactos del modelo (`.joblib`, `.json`). Este paso asegura que el proceso de entrenamiento no esté roto.
    4.  **Build de Docker:** Construye la imagen Docker dentro del runner de GitHub.
    5.  **Ejecución del Contenedor:** Levanta el contenedor en segundo plano.
    6.  **Pruebas Automatizadas:** Ejecuta el script `tests/test_api.py` contra el contenedor en ejecución, probando los endpoints en un entorno realista.
    7.  **Limpieza:** Detiene y elimina el contenedor de prueba.
  * **Job de Despliegue (`deploy`):**
    1.  **Condicional:** Este job depende del éxito del job `test` y **solo se ejecuta en un `push` directo a `main`**, previniendo despliegues desde pull requests.
    2.  **Login:** Se autentica de forma segura en Docker Hub usando secretos de GitHub (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`).
    3.  **Build and Push:** Utiliza la acción `docker/build-push-action` para construir la imagen y subirla al registro de Docker Hub con el tag `latest`.

Este flujo garantiza que cada cambio en la rama principal sea automáticamente probado y, si pasa las pruebas, desplegado como una nueva imagen de Docker, logrando una verdadera **Integración y Entrega Continua**.

-----

## 📜 5. Documentación y Entrega

La documentación y la estructura del proyecto fueron diseñadas para ser claras, completas y seguir las mejores prácticas.

  * **README.md:** El archivo `README.md` principal es una guía completa que explica cómo configurar el entorno, entrenar el modelo, ejecutar la API (localmente y con Docker) y cómo probar los endpoints con ejemplos de `curl`.
  * **Código Documentado:** El código fuente incluye comentarios explicativos en las funciones y clases clave.
  * **Pruebas Explícitas:** El directorio `tests/` contiene pruebas automatizadas que no solo validan el funcionamiento del sistema, sino que también sirven como documentación viva de cómo debe comportarse la API.
  * **Reflexiones Finales:**
      * **Logros:** Se ha creado un sistema MLOps funcional y robusto que es reproducible, escalable y automatizado. La separación de componentes permite que el equipo de ciencia de datos actualice el modelo (`/model`) sin afectar al equipo de backend que gestiona la API (`/api`).
      * **Posibles Mejoras:** Para un entorno productivo, los siguientes pasos incluirían: versionado de modelos en un registro como MLflow, un sistema de monitoreo de predicciones para detectar *data drift*, y el despliegue en una plataforma en la nube como Kubernetes o AWS App Runner para una mayor escalabilidad y gestión.
