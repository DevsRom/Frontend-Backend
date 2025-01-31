from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import os

router = APIRouter()

DATA_DIR = "/Users/user/SCOUTVISION/iDATAi/FronBackend_210125/Backend-api/data"  # ✅ Verifica que esta ruta es la correcta

@router.get("/get_bathymetric_points/")
def get_bathymetric_points():
    """📡 Devuelve los puntos batimétricos almacenados en el último archivo CSV"""
    if not os.path.exists(DATA_DIR):
        raise HTTPException(status_code=404, detail="❌ Carpeta de datos no encontrada.")

    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if not csv_files:
        raise HTTPException(status_code=404, detail="❌ No se encontraron archivos CSV en la carpeta de datos.")

    latest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join(DATA_DIR, f)))  # 🔹 Buscar el más reciente
    file_path = os.path.join(DATA_DIR, latest_file)

    print(f"✅ Leyendo archivo CSV: {file_path}")  # 🔹 Agrega logs para depuración

    df = pd.read_csv(file_path, sep=None, engine="python")  # Detecta automáticamente el delimitador

    if "latitude" not in df.columns or "longitude" not in df.columns or "depth" not in df.columns:
        raise HTTPException(status_code=400, detail="❌ El archivo no tiene las columnas requeridas.")

    df["depth"] = df["depth"].apply(lambda x: x if x == 0 else -abs(x))  # 🔹 Asegurar valores negativos en depth

    return {"points": df.to_dict(orient="records")}

# 🔹 Asegurar que la carpeta data existe
os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/upload_bathymetry/")
async def upload_bathymetry(file: UploadFile = File(...)):
    """📂 Guarda el archivo CSV recibido y devuelve la confirmación."""
    file_path = os.path.join(DATA_DIR, "data.csv")

    try:
        # ✅ Guardar el archivo en la carpeta /data/
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # ✅ Leer el CSV para verificar su estructura
        df = pd.read_csv(file_path, sep=";", engine="python")

        if "latitude" not in df.columns or "longitude" not in df.columns or "depth" not in df.columns:
            raise HTTPException(status_code=400, detail="❌ El archivo no contiene las columnas requeridas: latitude, longitude, depth.")

        # 🔹 Convertir valores de depth a negativos (excepto 0)
        df["depth"] = df["depth"].apply(lambda x: x if x == 0 else -abs(x))
        
        # ✅ Guardar el archivo corregido
        df.to_csv(file_path, sep=";", index=False)

        return {"message": f"✅ Archivo '{file.filename}' guardado y corregido en {file_path}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error al procesar el archivo: {str(e)}")