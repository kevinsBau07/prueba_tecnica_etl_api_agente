import requests
import pandas as pd
from sqlalchemy import create_engine

# === 1. Consultar datos desde la API ===
url = "https://datosabiertos.bogota.gov.co/api/3/action/datastore_search"
params = {
    "resource_id": "00081edc-cd17-4fe3-9013-10719a444334",  # dataset
    "limit": 50
}

response = requests.get(url, params=params)
data = response.json()
records = data["result"]["records"]

# === 2. Convertir a DataFrame ===
df = pd.DataFrame(records)

# Convertir la columna a numérica
df["TOTAL ESTUDIANTES ATENDIDOS"] = pd.to_numeric(df["TOTAL ESTUDIANTES ATENDIDOS"], errors="coerce")

# Ordenar por la columna de menor a mayor
df_sorted = df.sort_values(by="TOTAL ESTUDIANTES ATENDIDOS", ascending=True)
#print(df_sorted)

# === 3. Conexión a PostgreSQL ===
# Cambia usuario, contraseña, base de datos y puerto según tu configuración
#engine = create_engine("postgresql://postgres:Kevinssanti@localhost:5432/datosestudiantesdb")
#from sqlalchemy import create_engine

#engine = create_engine("postgresql+psycopg2://postgres:K07evinssanti@localhost:5432/postgres")
engine = create_engine(
    "postgresql+psycopg2://postgres:K07evinssanti@127.0.0.1:5432/datosestudiantesdb"
)

# === 4. Guardar en PostgreSQL ===
# Guarda en una tabla llamada "estudiantes_atendidos"
df_sorted.to_sql("estudiantes_atendidos", engine, if_exists="replace", index=False)

print("✅ Datos ordenados guardados en PostgreSQL en la tabla 'estudiantes_atendidos'")
