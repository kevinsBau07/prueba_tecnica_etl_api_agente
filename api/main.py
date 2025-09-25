from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
import pandas as pd
import requests

# ==============================
# 1. Conexión a PostgreSQL
# ==============================
DATABASE_URL = "postgresql://postgres:K07evinssanti@localhost:5432/datosestudiantesdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)

# Cargar la tabla existente en la BD
estudiantes_table = Table("estudiantes_atendidos", metadata, autoload_with=engine)

# ==============================
# 2. Inicializar la API
# ==============================
app = FastAPI(title="API Estudiantes Atendidos")

# Token sencillo para proteger el endpoint de actualización
API_TOKEN = "mi_token_secreto"

# ==============================
# 3. Dependencia para sesión
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================
# 4. Endpoints
# ==============================

# Listar todos los registros
@app.get("/registros")
def listar_registros(db=Depends(get_db)):
    query = estudiantes_table.select()
    result = db.execute(query).fetchall()
    return [dict(r._mapping) for r in result]

# Consultar un registro por _id
@app.get("/registros/{id}")
def obtener_registro(id: int, db=Depends(get_db)):
    query = estudiantes_table.select().where(estudiantes_table.c._id == id)
    result = db.execute(query).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return dict(result._mapping)

# Buscar por palabra clave en la columna "INSTITUCION EDUCATIVA DISTRITAL"
@app.get("/buscar")
def buscar(keyword: str, db=Depends(get_db)):
    query = estudiantes_table.select().where(
        estudiantes_table.c["INSTITUCION EDUCATIVA DISTRITAL"].ilike(f"%{keyword}%")
    )
    result = db.execute(query).fetchall()
    return [dict(r._mapping) for r in result]

# Endpoint protegido para actualizar datos desde el ETL
@app.post("/actualizar")
def actualizar(token: str):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Obtener datos desde la API de datos abiertos
    url = "https://datosabiertos.bogota.gov.co/api/3/action/datastore_search"
    params = {"resource_id": "00081edc-cd17-4fe3-9013-10719a444334", "limit": 50}
    data = requests.get(url, params=params).json()["result"]["records"]

    df = pd.DataFrame(data)

    # Asegurar tipo numérico en la columna TOTAL ESTUDIANTES ATENDIDOS
    df["TOTAL ESTUDIANTES ATENDIDOS"] = pd.to_numeric(
        df["TOTAL ESTUDIANTES ATENDIDOS"], errors="coerce"
    )

    # Ordenar antes de guardar
    df_sorted = df.sort_values(by="TOTAL ESTUDIANTES ATENDIDOS", ascending=True)

    # Guardar en PostgreSQL (reemplazar tabla)
    df_sorted.to_sql("estudiantes_atendidos", engine, if_exists="replace", index=False)

    return {"status": "ok", "message": "Datos actualizados correctamente"}
