"""
Script: download_data.py
Descripción:
    Descarga los datos de incidentes viales de AXA México (2018–2024)
    desde https://files.i2ds.org/OpenDataAxaMx/, los descomprime,
    concatena y guarda en data/raw/axa/.

    También genera un archivo de texto con información sobre las fuentes y
    la fecha de descarga.

Uso:
    python src/proyecto_ing_datos/data/download_data.py
"""

import os
import requests
import zipfile
import io
import pandas as pd
from datetime import datetime

from proyecto_ciencia_de_datos.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

# === Directorios ===
RAW_DIR_AXA = RAW_DATA_DIR / "axa"
RAW_DIR_INEGI = RAW_DATA_DIR / "inegi"
RAW_DIR_WEATHER = RAW_DATA_DIR / "weather"
INFO_FILE_AXA = os.path.join(RAW_DIR_AXA, "fuentes_info.txt")
INFO_FILE_INEGI = os.path.join(RAW_DIR_INEGI, "fuentes_info.txt")
INFO_FILE_WEATHER = os.path.join(RAW_DIR_WEATHER, "fuentes_info.txt")

# === Columnas oficiales según AXA ===
COLUMNAS = [
    "SINIESTRO","LATITUD","LONGITUD","CODIGO POSTAL","CALLE","COLONIA",
    "CAUSA SINIESTRO","TIPO VEHICULO","COLOR","MODELO","NIVEL DAÑO VEHICULO",
    "PUNTO DE IMPACTO","AÑO","MES","DÍA NUMERO","DIA","HORA","ESTADO","CIUDAD",
    "LESIONADOS","RELACION LESIONADOS","EDAD LESIONADO","GENERO LESIONADO",
    "NIVEL LESIONADO","HOSPITALIZADO","FALLECIDO","AMBULANCIA","ARBOL",
    "PIEDRA","DORMIDO","GRUA","OBRA CIVIL","PAVIMENTO MOJADO","EXPLOSION LLANTA",
    "VOLCADURA","PERDIDA TOTAL","CONDUCTOR DISTRAIDO","FUGA","ALCOHOL",
    "MOTOCICLETA","BICICLETA","SEGURO","TAXI","ANIMAL"
]

def descargar_datos_axa():
    """
    Descarga los archivos ZIP de incidentes viales de AXA (2018–2024)
    y guarda los CSV sin procesar en data/raw/axa.
    """
    os.makedirs(RAW_DIR_AXA, exist_ok=True)
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for year in range(2018, 2025):
        url = f"https://files.i2ds.org/OpenDataAxaMx/incidentes_viales_{year}_axa.zip"
        print(f"⬇️ Descargando datos de {year} ...")

        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
                output_path = os.path.join(RAW_DIR_AXA, f"incidentes_viales_{year}_axa.csv")

                with z.open(csv_name) as source, open(output_path, "wb") as target:
                    target.write(source.read())

            print(f"✅ Archivo {year} guardado en: {output_path}")

        except Exception as e:
            print(f"⚠️ Error al descargar o guardar {year}: {e}")

    # Guardar metadatos de descarga
    with open(INFO_FILE_AXA, "a", encoding="utf-8") as f:
        f.write("Fuente: AXA México – OpenData Incidentes Viales\n")
        f.write("URL: https://i2ds.org/datos-abiertos/\n")
        f.write("Rango de años: 2018–2024\n")
        f.write(f"Fecha de descarga: {hoy}\n")
        f.write(f"Archivos guardados en: {RAW_DIR_AXA}\n\n")


def descarga_datos_inegi():
    """
    Descarga los datos de accidentes de tránsito terrestre del INEGI
    """
    url = 'https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/conjunto_de_datos_atus_anual_csv.zip'
    os.makedirs(RAW_DIR_INEGI, exist_ok=True)
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("⬇️ Descargando datos del INEGI ...")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        z.extractall(RAW_DIR_INEGI)
        print(f"✅ Datos del INEGI descargados y descomprimidos en: {RAW_DIR_INEGI}")

        # Registrar metadatos de descarga
        with open(INFO_FILE_INEGI, "a", encoding="utf-8") as f:
            f.write("Fuente: INEGI – Accidentes de Tránsito Terrestre\n")
            f.write("URL: https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/\n")
            f.write(f"Fecha de descarga: {hoy}\n")
            f.write(f"Directorio guardado: {RAW_DIR_INEGI}\n\n")

    except Exception as e:
        print(f"⚠️ Error al descargar o descomprimir datos del INEGI: {e}")

def descarga_datos_weather():
    """
    Descarga datos climáticos históricos de Open Meteo
    """
    url_weather = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 29.1026,
        "longitude": -110.9773,
        "hourly": ["temperature_2m", "rain", "showers", "visibility"],
        "start": "2018-01-01T00:00",
        "end": "2024-12-31T23:00",
        "timezone": "America/Mazatlan"
    }
    os.makedirs(RAW_DIR_WEATHER, exist_ok=True)
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("⬇️ Descargando datos climáticos de Open Meteo ...")
    try:
        resp = requests.get(url_weather, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Convertir a DataFrame
        df_weather = pd.DataFrame(data['hourly'])
        output_file = os.path.join(RAW_DIR_WEATHER, "weather_data_2018_2024.csv")
        df_weather.to_csv(output_file, index=False)
        print(f"✅ Datos climáticos guardados en: {output_file}")
        print(f"   {len(df_weather):,} filas x {len(df_weather.columns)} columnas")

        # Registrar metadatos de descarga
        with open(INFO_FILE_WEATHER, "a", encoding="utf-8") as f:
            f.write("Fuente: Open Meteo – Historical Weather Data\n")
            f.write("URL: https://open-meteo.com/\n")
            f.write(f"Rango de fechas: 2018-01-01 a 2024-12-31\n")
            f.write(f"Fecha de descarga: {hoy}\n")
            f.write(f"Archivo guardado: {output_file}\n\n")

    except Exception as e:
        print(f"⚠️ Error al descargar datos climáticos de Open Meteo: {e}")

if __name__ == "__main__":
    descargar_datos_axa()
    descarga_datos_inegi()
    descarga_datos_weather()