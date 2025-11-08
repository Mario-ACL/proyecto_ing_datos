"""
Este script es para aplicar los resultados de notebooks\1.01-EDA-processed-1.ipynb

y guardar los dataframes procesados.
"""

from proyecto_ciencia_de_datos.config import PROCESSED_DATA_DIR
import pandas as pd

print("\n" + "="*60)
print("🧹 Quitando Outliers...")
print("="*60)

axa_df = pd.read_csv(PROCESSED_DATA_DIR / 'axa_tidy.csv', sep=',', header='infer', low_memory=False)
inegi_df = pd.read_csv(PROCESSED_DATA_DIR / 'inegi_tidy.csv', sep=',', header='infer')
weather_df = pd.read_csv(PROCESSED_DATA_DIR / 'weather_tidy.csv', sep=',', header='infer')




# AXA

axa_df["ESTADO"] = (
    axa_df["ESTADO"]
    .astype(str)
    .str.strip()
    .str.lower()
)
axa_df = axa_df[axa_df['ESTADO'] == 'sonora']
axa_df.head()

axa_df = axa_df.drop(columns=[
    'ESTADO', # Ya que solo se tienen datos de Sonora
    'EDAD LESIONADO', 
    'PUNTO DE IMPACTO', 
    'GENERO LESIONADO', 
    'COLOR', 
    'CODIGO POSTAL', 
    'CALLE', 
    'COLONIA', 
    'DÍA NUMERO', 
    'RELACION LESIONADOS', 
    'NIVEL LESIONADO',
    'NIVEL DAÑO VEHICULO'])

axa_df[['MES', 'CIUDAD']] = axa_df[['MES', 'CIUDAD']].astype('category')

axa_df['CAUSA SINIESTRO'] = axa_df['CAUSA SINIESTRO'].fillna('Sin dato')
axa_df['TIPO VEHICULO'] = axa_df['TIPO VEHICULO'].fillna(axa_df['TIPO VEHICULO'].mode()[0])
axa_df['MODELO'] = axa_df['MODELO'].fillna(axa_df['MODELO'].mode()[0])
axa_df[['CAUSA SINIESTRO', 'TIPO VEHICULO']] = axa_df[['CAUSA SINIESTRO', 'TIPO VEHICULO']].astype('category')

axa_df['MODELO'] = axa_df['MODELO'].apply(lambda x: 'Sin Dato' if x < 1900 or x > 2024 else str(int(x)))


# INEGI
inegi_df = inegi_df[inegi_df['ID_ENTIDAD'] == 26]
inegi_df = inegi_df.drop(columns=['ID_ENTIDAD']) # Solo Sonora
inegi_df['ID_DIA'].replace(0, 32)

# WEATHER

# Nada

# GUARDAR LOS DATAFRAMES PROCESADOS

axa_df.to_csv(PROCESSED_DATA_DIR / 'axa_EDA_son.csv', index=False)

inegi_df.to_csv(PROCESSED_DATA_DIR / 'inegi_EDA_son.csv', index=False)

print("\n" + "="*60)
print("Ya no hay outliers...")
print("="*60)

print(f"\nArchivos generados en: {PROCESSED_DATA_DIR}/")
print("  - axa_EDA_son.csv")
print("  - inegi_EDA_son.csv")
# print("  - weather_tidy.csv")
# print("  - reporte_procesamiento.txt")