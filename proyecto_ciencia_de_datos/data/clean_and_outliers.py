"""
Este script es para aplicar los resultados de notebooks\1.01-EDA-processed-1.ipynb

y guardar los dataframes procesados.
"""

from proyecto_ciencia_de_datos.config import PROCESSED_DATA_DIR
import pandas as pd
import unicodedata

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

axa_df = axa_df.drop(columns=['EDAD LESIONADO', 
                              'PUNTO DE IMPACTO', 
                              'GENERO LESIONADO', 
                              'COLOR', 
                              'CODIGO POSTAL', 
                              'CALLE', 
                              'COLONIA', 
                              'DÍA NUMERO', 
                              'RELACION LESIONADOS', 
                              'NIVEL LESIONADO', 
                              'NIVEL DAÑO VEHICULO', 
                              'GRUA', 
                              'SEGURO',
                              'PERDIDA TOTAL',
                              'VOLCADURA',
                              'OBRA CIVIL',
                              'AMBULANCIA',
                              'ARBOL',
                              'PIEDRA',
                              'DORMIDO',
                              'PAVIMENTO MOJADO',
                              'ANIMAL',
                              'EXPLOSION LLANTA',
                              'CONDUCTOR DISTRAIDO',
                              'ALCOHOL',
                              'MOTOCICLETA',
                              'BICICLETA',
                              'HOSPITALIZADO',
                              'FALLECIDO',
                              'FUGA',
                              'TAXI',
                              'MES',
                              'ESTADO']) # Solo Sonora

axa_df['CAUSA SINIESTRO'] = axa_df['CAUSA SINIESTRO'].fillna('Sin dato')
axa_df['TIPO VEHICULO'] = axa_df['TIPO VEHICULO'].fillna(axa_df['TIPO VEHICULO'].mode()[0])
axa_df['MODELO'] = axa_df['MODELO'].fillna(axa_df['MODELO'].mode()[0])

cat_cols = ['CAUSA SINIESTRO', 'TIPO VEHICULO', 'DIA', 'CIUDAD']
for col in cat_cols:
    axa_df[col] = axa_df[col].astype('category')

axa_df['MODELO'] = axa_df['MODELO'].apply(lambda x: 0 if x < 1900 or x > 2024 else int(x))


# INEGI
def _normalize_text_remove_accents(val):
    if pd.isna(val):
        return val
    s = str(val).strip().lower()
    return ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')

inegi_df['DIASEMANA'] = inegi_df['DIASEMANA'].apply(_normalize_text_remove_accents)

inegi_df = inegi_df[inegi_df['ID_ENTIDAD'] == 26]
inegi_df = inegi_df.drop(columns=[
    'ID_ENTIDAD', 'CONDMUERTO', 'CONDHERIDO', 'PASAMUERTO', 'PASAHERIDO',
    'PEATMUERTO', 'PEATHERIDO', 'CICLMUERTO', 'CICLHERIDO', 'OTROMUERTO',
    'OTROHERIDO', 'NEMUERTO', 'NEHERIDO', 'TRANVIA'])
inegi_df['ID_DIA'].replace(0, 32)
inegi_df = inegi_df[inegi_df['SEXO'] != 'Certificado cero']
cat_cols = [
    'TIPACCID',
    'CAUSAACCI',
    'DIASEMANA',
    'URBANA',
    'SUBURBANA',
    'CAPAROD',
    'SEXO',
    'ALIENTO'
]
# Convertir a categoría
for col in cat_cols:
    inegi_df[col] = inegi_df[col].astype('category')

# WEATHER
weather_df.dropna(inplace=True)

# GUARDAR LOS DATAFRAMES PROCESADOS

axa_df.to_csv(PROCESSED_DATA_DIR / 'axa_EDA_son.csv', index=False)

inegi_df.to_csv(PROCESSED_DATA_DIR / 'inegi_EDA_son.csv', index=False)

weather_df.to_csv(PROCESSED_DATA_DIR / 'weather_EDA_son.csv', index=False)

print("\n" + "="*60)
print("Ya no hay outliers...")
print("="*60)

print(f"\nArchivos generados en: {PROCESSED_DATA_DIR}/")
print("  - axa_EDA_son.csv")
print("  - inegi_EDA_son.csv")
print("  - weather_tidy.csv")
# print("  - reporte_procesamiento.txt")