"""
Preparación de datos - Medical Insurance Dataset
Proyecto de demostración para entrevista en sector asegurador
"""

import pandas as pd


# ─────────────────────────────────────────────
# 1. CARGA Y LIMPIEZA
# ─────────────────────────────────────────────

df = pd.read_csv("insurance.csv")

# Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Eliminar nulos y duplicados
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

print(f"Filas tras limpieza: {len(df)}")


# ─────────────────────────────────────────────
# 2. COLUMNAS CALCULADAS
# ─────────────────────────────────────────────

# segmento_edad
def segmentar_edad(edad):
    if edad <= 30:
        return "Joven"
    elif edad <= 45:
        return "Adulto"
    elif edad <= 60:
        return "Senior"
    else:
        return "Mayor"

df["segmento_edad"] = df["age"].apply(segmentar_edad)

# nivel_prima
def nivel_prima(charges):
    if charges < 5000:
        return "Baja"
    elif charges <= 15000:
        return "Media"
    else:
        return "Alta"

df["nivel_prima"] = df["charges"].apply(nivel_prima)

# fumador_flag
df["fumador_flag"] = df["smoker"].map({"yes": 1, "no": 0})


# ─────────────────────────────────────────────
# 3. EXPORTACIÓN A EXCEL
# ─────────────────────────────────────────────

output_path = "insurance_clean.xlsx"

with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Datos")

print(f"\nArchivo exportado: {output_path}")


# ─────────────────────────────────────────────
# 4. RESUMEN FINAL
# ─────────────────────────────────────────────

print(f"\n{'='*45}")
print(f"  RESUMEN DEL DATASET LIMPIO")
print(f"{'='*45}")
print(f"  Filas    : {df.shape[0]}")
print(f"  Columnas : {df.shape[1]}")
print(f"{'='*45}")
print("\nPreview:")
print(df.head(5).to_string(index=False))
