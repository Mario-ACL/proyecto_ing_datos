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
from datetime import datetime

# === Directorios ===
RAW_DIR_AXA = "data/raw/axa"
RAW_DIR_INEGI = "data/raw/inegi/conjunto_de_datos"
RAW_DIR_WEATHER = "data/raw/weather"
PROCESSED_DIR = "data/processed"

# Crear directorio de salida
os.makedirs(PROCESSED_DIR, exist_ok=True)


def tidy_axa_data():
    """
    Limpia y transforma datos de AXA a formato tidy
    """
    print("\n" + "="*60)
    print("🧹 Limpiando datos de AXA...")
    print("="*60)
    
    input_file = os.path.join(RAW_DIR_AXA, "incidentes_viales_2018_2024.csv")
    
    if not os.path.exists(input_file):
        print(f"⚠️ Archivo no encontrado: {input_file}")
        return None
    
    # Leer datos
    df = pd.read_csv(input_file, low_memory=False)
    print(f"📊 Datos originales: {len(df):,} filas x {df.shape[1]} columnas")
    
    # Limpieza básica
    print("🔧 Aplicando limpieza...")
    
    # 1. Eliminar duplicados
    df_clean = df.drop_duplicates()
    print(f"   ✓ Duplicados eliminados: {len(df) - len(df_clean):,}")
    
    # 2. Limpiar nombres de columnas
    df_clean.columns = df_clean.columns.str.strip().str.upper()
    
    # 3. Convertir tipos de datos
    # Coordenadas
    if 'LATITUD' in df_clean.columns:
        df_clean['LATITUD'] = pd.to_numeric(df_clean['LATITUD'], errors='coerce')
    if 'LONGITUD' in df_clean.columns:
        df_clean['LONGITUD'] = pd.to_numeric(df_clean['LONGITUD'], errors='coerce')
    
    # Fechas y tiempos
    if 'AÑO' in df_clean.columns:
        df_clean['AÑO'] = pd.to_numeric(df_clean['AÑO'], errors='coerce')
    if 'MES' in df_clean.columns:
        df_clean['MES'] = pd.to_numeric(df_clean['MES'], errors='coerce')
    
    # # 4. Crear columna de fecha-hora si es posible
    # try:
    #     df_clean['FECHA'] = pd.to_datetime(
    #         df_clean['AÑO'].astype(str) + '-' + 
    #         df_clean['MES'].astype(str).str.zfill(2) + '-' + 
    #         df_clean['DÍA NUMERO'].astype(str).str.zfill(2),
    #         errors='coerce'
    #     )
    # except:
    #     print("   ⚠️ No se pudo crear columna FECHA")
    
    # 5. Convertir columnas binarias (SI/NO) a booleanos
    binary_cols = ['HOSPITALIZADO', 'FALLECIDO', 'AMBULANCIA', 'ARBOL', 'PIEDRA',
                   'DORMIDO', 'GRUA', 'OBRA CIVIL', 'PAVIMENTO MOJADO', 
                   'EXPLOSION LLANTA', 'VOLCADURA', 'PERDIDA TOTAL',
                   'CONDUCTOR DISTRAIDO', 'FUGA', 'ALCOHOL', 'MOTOCICLETA',
                   'BICICLETA', 'SEGURO', 'TAXI', 'ANIMAL']
    
    for col in binary_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].map({'SI': True, 'NO': False}).astype('boolean')
    
    # 6. Eliminar filas sin coordenadas válidas
    df_clean = df_clean.dropna(subset=['LATITUD', 'LONGITUD'])
    print(f"   ✓ Filas con coordenadas válidas: {len(df_clean):,}")
    
    # Guardar
    output_file = os.path.join(PROCESSED_DIR, "axa_tidy.csv")
    df_clean.to_csv(output_file, index=False)
    print(f"✅ Datos de AXA guardados en: {output_file}")
    print(f"   {len(df_clean):,} filas x {df_clean.shape[1]} columnas\n")
    
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
            df = pd.read_csv(file, encoding='latin1', low_memory=False)
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