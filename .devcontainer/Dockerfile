# 1. Imagen Base (Python 3.11 en Debian Bookworm)
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

# 2. Configuración de entorno
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# 3. Dependencias de Sistema (Esenciales para Geopandas, Graphviz y C++)
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libproj-dev \
    g++ \
    graphviz \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. Instalación de Pesos Pesados (Versión CPU para ahorrar espacio y evitar errores de drivers)
RUN pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip3 install --no-cache-dir tensorflow-cpu

# 5. Resto del Stack (Consolidado y sin duplicados)
RUN pip3 install --no-cache-dir \
    # Core Data Science & Stats
    pandas numpy scipy sqlalchemy statsmodels \
    # Visualization
    matplotlib seaborn plotly nbformat \
    # Geospatial Engine
    geopandas contextily pyproj shapely h3>=4.0.0 keplergl folium alphashape \
    # ML & Optimización
    scikit-learn hdbscan shap xgboost optuna \
    # Google Cloud Stack
    google-cloud-storage google-cloud-bigquery pandas-gbq google-cloud-bigquery-storage pyarrow \
    # Jupyter Helpers & Others
    ipykernel ipywidgets pyjokes graphviz