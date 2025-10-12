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

# === Directorios ===
RAW_DIR = "data/raw/axa"
INFO_FILE = os.path.join("../../data/raw", "/fuentes_info.txt")

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
    os.makedirs(RAW_DIR, exist_ok=True)
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dfs = []

    for year in range(2018, 2025):
        url = f"https://files.i2ds.org/OpenDataAxaMx/incidentes_viales_{year}_axa.zip"
        print(f"⬇️ Descargando {year} ...")

        try:
            resp = requests.get(url)
            resp.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(resp.content))

            csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
            with z.open(csv_name) as f:
                if year < 2020:
                    df = pd.read_csv(f, encoding="latin1", low_memory=False)
                else:
                    df = pd.read_csv(f, header=None, names=COLUMNAS, encoding="latin1", low_memory=False)

                df = df.replace({"\\N": pd.NA, " ": pd.NA, "": pd.NA})
                df["AÑO"] = year
                dfs.append(df)

        except Exception as e:
            print(f"⚠️ Error al procesar {year}: {e}")

    axa_all = pd.concat(dfs, ignore_index=True)
    output_file = os.path.join(RAW_DIR, "incidentes_viales_2018_2024.csv")
    axa_all.to_csv(output_file, index=False)
    print(f"✅ Archivo combinado guardado en: {output_file}")
    print(f"   {len(axa_all):,} filas x {len(axa_all.columns)} columnas")

    # Registrar metadatos de descarga
    with open(INFO_FILE, "a", encoding="utf-8") as f:
        f.write("Fuente: AXA México – OpenData Incidentes Viales\n")
        f.write("URL: https://files.i2ds.org/OpenDataAxaMx/\n")
        f.write(f"Rango de años: 2018–2024\n")
        f.write(f"Fecha de descarga: {hoy}\n")
        f.write(f"Archivo guardado: {output_file}\n\n")


def descarga_datos_inegi():
    """
    Descarga los datos de accidentes de tránsito terrestre del INEGI
    """
    url = 'https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/conjunto_de_datos_atus_anual_csv.zip'
    raw_dir = "../../data/raw/inegi/"
    INFO_FILE = os.path.join(raw_dir, "fuentes_info.txt")
    os.makedirs(raw_dir, exist_ok=True)
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("⬇️ Descargando datos del INEGI ...")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        z.extractall(raw_dir)
        print(f"✅ Datos del INEGI descargados y descomprimidos en: {raw_dir}")

        # Registrar metadatos de descarga
        with open(INFO_FILE, "a", encoding="utf-8") as f:
            f.write("Fuente: INEGI – Accidentes de Tránsito Terrestre\n")
            f.write("URL: https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/\n")
            f.write(f"Fecha de descarga: {hoy}\n")
            f.write(f"Directorio guardado: {raw_dir}\n\n")

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
    raw_dir = "../../data/raw/weather/"
    INFO_FILE = os.path.join(raw_dir, "fuentes_info.txt")
    os.makedirs(raw_dir, exist_ok=True)
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("⬇️ Descargando datos climáticos de Open Meteo ...")
    try:
        resp = requests.get(url_weather, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Convertir a DataFrame
        df_weather = pd.DataFrame(data['hourly'])
        output_file = os.path.join(raw_dir, "weather_data_2018_2024.csv")
        df_weather.to_csv(output_file, index=False)
        print(f"✅ Datos climáticos guardados en: {output_file}")
        print(f"   {len(df_weather):,} filas x {len(df_weather.columns)} columnas")

        # Registrar metadatos de descarga
        with open(INFO_FILE, "a", encoding="utf-8") as f:
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
