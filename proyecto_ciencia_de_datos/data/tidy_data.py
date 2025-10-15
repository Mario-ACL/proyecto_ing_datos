"""
Script: tidy_data.py
Descripción:
    Limpia y transforma los datos crudos de AXA, INEGI y Weather
    a formato tidy (largo) y los guarda en data/processed/

Uso:
    python proyecto_ciencia_de_datos/tidy_data.py
"""

import os
import pandas as pd
import glob
import csv
from datetime import datetime
from proyecto_ciencia_de_datos.config import PROCESSED_DATA_DIR, RAW_DATA_DIR


# === Directorios ===
RAW_DIR_AXA = RAW_DATA_DIR / "axa"
RAW_DIR_INEGI = RAW_DATA_DIR / "inegi/conjunto_de_datos"
RAW_DIR_WEATHER = RAW_DATA_DIR / "weather"
PROCESSED_DIR = PROCESSED_DATA_DIR

# Crear directorio de salida
os.makedirs(PROCESSED_DIR, exist_ok=True)

def tidy_axa_data():
    """
    Combina todos los CSV de AXA en data/raw/axa y aplica limpieza y transformación
    para generar un conjunto de datos tidy en data/processed/axa_tidy.csv
    """

    # === Columnas base del 2018 (referencia oficial AXA) ===
    BASE_COLUMNS = [
        "SINIESTRO","LATITUD","LONGITUD","CODIGO POSTAL","CALLE","COLONIA",
        "CAUSA SINIESTRO","TIPO VEHICULO","COLOR","MODELO","NIVEL DAÑO VEHICULO",
        "PUNTO DE IMPACTO","AÑO","MES","DÍA NUMERO","DIA","HORA","ESTADO","CIUDAD",
        "LESIONADOS","RELACION LESIONADOS","EDAD LESIONADO","GENERO LESIONADO",
        "NIVEL LESIONADO","HOSPITALIZADO","FALLECIDO","AMBULANCIA","ARBOL",
        "PIEDRA","DORMIDO","GRUA","OBRA CIVIL","PAVIMENTO MOJADO",
        "EXPLOSION LLANTA","VOLCADURA","PERDIDA TOTAL","CONDUCTOR DISTRAIDO",
        "FUGA","ALCOHOL","MOTOCICLETA","BICICLETA","SEGURO","TAXI","ANIMAL"
    ]

    print("\n" + "="*70)
    print("📦 Combinando y limpiando datos de AXA")
    print("="*70)

    # === Buscar archivos CSV ===
    csv_files = [f for f in os.listdir(RAW_DIR_AXA) if f.endswith(".csv")]
    if not csv_files:
        print("⚠️ No se encontraron archivos CSV en data/raw/axa/")
        return None

    print(f"📂 Archivos encontrados: {len(csv_files)}")

    dfs = []

    for file in sorted(csv_files):
        file_path = os.path.join(RAW_DIR_AXA, file)
        print(f"\n📥 Leyendo {file} ...")

        try:
            # Detectar si tiene encabezado
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            has_header = "SINIESTRO" in first_line.upper()

            # Detectar delimitador
            with open(file_path, "r", encoding="utf-8") as f:
                sniffer = csv.Sniffer()
                sample = f.read(2048)
                try:
                    dialect = sniffer.sniff(sample)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ","
            print(f"   • Delimitador detectado: '{delimiter}' | Encabezado: {has_header}")

            # Leer CSV con configuración adecuada
            if has_header:
                df = pd.read_csv(file_path, sep=delimiter, encoding="utf-8", low_memory=False)
            else:
                df = pd.read_csv(file_path, sep=delimiter, encoding="utf-8", header=None,
                                 names=BASE_COLUMNS, low_memory=False)

            # Corregir si el archivo tiene columnas de más o de menos
            missing_cols = [c for c in BASE_COLUMNS if c not in df.columns]
            extra_cols = [c for c in df.columns if c not in BASE_COLUMNS]

            if missing_cols:
                print(f"   ⚠️ {len(missing_cols)} columnas faltantes → se rellenan con NaN")
                for c in missing_cols:
                    df[c] = pd.NA
            if extra_cols:
                print(f"   ⚠️ {len(extra_cols)} columnas extra → se eliminan: {extra_cols}")
                df = df.drop(columns=extra_cols, errors="ignore")

            # Reordenar columnas consistentemente
            df = df[BASE_COLUMNS]
            dfs.append(df)

        except Exception as e:
            print(f"⚠️ Error al leer {file}: {e}")

    if not dfs:
        print("❌ No se pudieron leer los archivos correctamente.")
        return None

    # === Combinar todos los DataFrames ===
    df = pd.concat(dfs, ignore_index=True)
    print(f"\n📊 Datos combinados: {len(df):,} filas x {df.shape[1]} columnas")

    # === Limpieza básica ===
    print("\n🧹 Iniciando limpieza de datos...")

    # 1. Eliminar duplicados
    df_clean = df.drop_duplicates()
    print(f"   ✓ Duplicados eliminados: {len(df) - len(df_clean):,}")

    # 2. Normalizar nombres de columnas
    df_clean.columns = df_clean.columns.str.strip().str.upper()

    # 3. Reemplazar valores vacíos
    df_clean = df_clean.replace({"\\N": pd.NA, " ": pd.NA, "": pd.NA})

    # 4. Convertir columnas numéricas
    for col in ["LATITUD", "LONGITUD", "AÑO", "MES"]:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # 5. Convertir columnas binarias (SI/NO → True/False), reemplazando vacíos con False
    binary_cols = [
        "HOSPITALIZADO","FALLECIDO","AMBULANCIA","ARBOL","PIEDRA","DORMIDO",
        "GRUA","OBRA CIVIL","PAVIMENTO MOJADO","EXPLOSION LLANTA","VOLCADURA",
        "PERDIDA TOTAL","CONDUCTOR DISTRAIDO","FUGA","ALCOHOL","MOTOCICLETA",
        "BICICLETA","SEGURO","TAXI","ANIMAL"
    ]

    for col in binary_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].map({"SI": True, "NO": False})
            df_clean[col] = df_clean[col].fillna(False).astype("boolean")

    # 6. Eliminar filas sin coordenadas válidas
    if "LATITUD" in df_clean.columns and "LONGITUD" in df_clean.columns:
        df_clean = df_clean.dropna(subset=["LATITUD", "LONGITUD"])
    print(f"   ✓ Filas con coordenadas válidas: {len(df_clean):,}")

    # === Guardar datos procesados ===
    output_file = os.path.join(PROCESSED_DIR, "axa_tidy.csv")
    df_clean.to_csv(output_file, index=False)
    print(f"\n✅ Datos tidy guardados en: {output_file}")
    print(f"   {len(df_clean):,} filas x {df_clean.shape[1]} columnas")

    # === Guardar metadatos del procesamiento ===
    log_file = os.path.join(PROCESSED_DIR, "info_tidy.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Procesamiento AXA – {datetime.now()}\n")
        f.write(f"Archivos combinados: {', '.join(csv_files)}\n")
        f.write(f"Archivo tidy en: {output_file}\n\n")

    return df_clean



def tidy_inegi_data(year_range=(2018, 2024)):
    """
    Limpia y concatena datos de INEGI a formato tidy
    
    Args:
        year_range: Tupla con (año_inicio, año_fin) para filtrar
    """
    print("\n" + "="*60)
    print("🧹 Limpiando datos de INEGI...")
    print("="*60)
    
    if not os.path.exists(RAW_DIR_INEGI):
        print(f"⚠️ Directorio no encontrado: {RAW_DIR_INEGI}")
        return None
    
    # Buscar todos los archivos CSV del INEGI
    pattern = os.path.join(RAW_DIR_INEGI, "atus_anual_*.csv")
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"⚠️ No se encontraron archivos CSV en: {RAW_DIR_INEGI}")
        return None
    
    print(f"📁 Archivos encontrados: {len(files)}")
    
    dfs = []
    year_start, year_end = year_range
    
    for file in files:
        # Extraer año del nombre del archivo
        filename = os.path.basename(file)
        try:
            year = int(filename.split('_')[-1].replace('.csv', ''))
        except:
            print(f"   ⚠️ No se pudo extraer año de: {filename}")
            continue
        
        # Filtrar por rango de años
        if year < year_start or year > year_end:
            continue
        
        print(f"   📖 Procesando {year}...")
        
        try:
            # Leer CSV (el INEGI usa latin1 típicamente)
            df = pd.read_csv(file, encoding='utf-8', index_col=False, low_memory=False)
            df['AÑO'] = year
            dfs.append(df)
            print(f"      ✓ {len(df):,} registros cargados")
        except Exception as e:
            print(f"      ⚠️ Error al leer {filename}: {e}")
    
    if not dfs:
        print("⚠️ No se pudieron cargar datos del INEGI")
        return None
    
    # Concatenar todos los años
    df_all = pd.concat(dfs, ignore_index=True)
    print(f"\n📊 Datos concatenados: {len(df_all):,} filas x {df_all.shape[1]} columnas")
    
    # Limpieza básica
    print("🔧 Aplicando limpieza...")
    
    # 1. Limpiar nombres de columnas
    df_all.columns = df_all.columns.str.strip().str.upper()
    
    # 2. Eliminar duplicados
    df_clean = df_all.drop_duplicates()
    print(f"   ✓ Duplicados eliminados: {len(df_all) - len(df_clean):,}")
    
    # 3. Convertir columnas numéricas comunes del INEGI
    numeric_cols = ['AÑO', 'MES', 'DIA', 'HORA']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Guardar
    output_file = os.path.join(PROCESSED_DIR, "inegi_tidy.csv")
    df_clean.to_csv(output_file, index=False)
    print(f"✅ Datos de INEGI guardados en: {output_file}")
    print(f"   {len(df_clean):,} filas x {df_clean.shape[1]} columnas\n")
    
    return df_clean


def tidy_weather_data():
    """
    Limpia y transforma datos climáticos a formato tidy
    """
    print("\n" + "="*60)
    print("🧹 Limpiando datos climáticos...")
    print("="*60)
    
    input_file = os.path.join(RAW_DIR_WEATHER, "weather_data_2018_2024.csv")
    
    if not os.path.exists(input_file):
        print(f"⚠️ Archivo no encontrado: {input_file}")
        return None
    
    # Leer datos
    df = pd.read_csv(input_file)
    print(f"📊 Datos originales: {len(df):,} filas x {df.shape[1]} columnas")
    
    # Limpieza
    print("🔧 Aplicando limpieza...")
    
    # 1. Convertir columna de tiempo a datetime
    df['time'] = pd.to_datetime(df['time'])
    
    # 2. Extraer componentes de fecha
    df['FECHA'] = df['time'].dt.date
    df['AÑO'] = df['time'].dt.year
    df['MES'] = df['time'].dt.month
    df['DIA'] = df['time'].dt.day
    df['HORA'] = df['time'].dt.hour
    
    # 3. Renombrar columnas a español
    rename_dict = {
        'time': 'FECHA_HORA',
        'temperature_2m': 'TEMPERATURA_C',
        'rain': 'LLUVIA_MM',
        'showers': 'ALTA_LLUVIA_MM',
        'visibility': 'VISIBILIDAD_M'
    }
    df = df.rename(columns=rename_dict)
    
    # 4. Eliminar duplicados
    df_clean = df.drop_duplicates()
    print(f"   ✓ Duplicados eliminados: {len(df) - len(df_clean):,}")
    
    # 5. Ordenar por fecha
    df_clean = df_clean.sort_values('FECHA_HORA').reset_index(drop=True)
    
    # Guardar
    output_file = os.path.join(PROCESSED_DIR, "weather_tidy.csv")
    df_clean.to_csv(output_file, index=False)
    print(f"✅ Datos climáticos guardados en: {output_file}")
    print(f"   {len(df_clean):,} filas x {df_clean.shape[1]} columnas\n")
    
    return df_clean


def generar_reporte():
    """
    Genera un reporte de resumen de los datos procesados
    """
    print("\n" + "="*60)
    print("📝 Generando reporte de procesamiento...")
    print("="*60)
    
    reporte_file = os.path.join(PROCESSED_DIR, "reporte_procesamiento.txt")
    
    with open(reporte_file, "w", encoding="utf-8") as f:
        f.write("REPORTE DE PROCESAMIENTO DE DATOS\n")
        f.write("="*60 + "\n")
        f.write(f"Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Información de cada dataset
        for dataset, filename in [
            ("AXA", "axa_tidy.csv"),
            ("INEGI", "inegi_tidy.csv"),
            ("Weather", "weather_tidy.csv")
        ]:
            filepath = os.path.join(PROCESSED_DIR, filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, low_memory=False)
                f.write(f"\n{dataset}:\n")
                f.write(f"  - Archivo: {filename}\n")
                f.write(f"  - Filas: {len(df):,}\n")
                f.write(f"  - Columnas: {df.shape[1]}\n")
                f.write(f"  - Columnas: {', '.join(df.columns[:10])}")
                if df.shape[1] > 10:
                    f.write(f", ... (+{df.shape[1]-10} más)")
                f.write("\n")
            else:
                f.write(f"\n{dataset}: No procesado\n")
    
    print(f"✅ Reporte guardado en: {reporte_file}\n")


def main():
    """
    Ejecuta todo el pipeline de limpieza
    """
    print("\n" + "🚀 INICIANDO PROCESAMIENTO DE DATOS" + "\n")
    
    # Procesar cada fuente de datos
    df_axa = tidy_axa_data()
    df_inegi = tidy_inegi_data(year_range=(2018, 2024))
    df_weather = tidy_weather_data()
    
    # Generar reporte
    generar_reporte()
    
    print("\n" + "="*60)
    print("✅ PROCESAMIENTO COMPLETADO")
    print("="*60)
    print(f"\nArchivos generados en: {PROCESSED_DIR}/")
    print("  - axa_tidy.csv")
    print("  - inegi_tidy.csv")
    print("  - weather_tidy.csv")
    print("  - reporte_procesamiento.txt")


if __name__ == "__main__":
    main()