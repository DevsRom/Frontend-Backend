from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

try:
    from app.routes.bathymetry import router as bathymetry_router
    from app.routes.tiles import router as tiles_router
except ImportError as e:
    print(f"❌ Error importando rutas: {e}")
    bathymetry_router = None
    tiles_router = None

app = FastAPI(title="API QGIS para Batimetría")

# 🔹 Habilitar CORS para permitir el acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Configurar carpeta de datos para servir archivos CSV al frontend
DATA_DIR = "/Users/user/SCOUTVISION/iDATAi/FronBackend_210125/Backend-api/data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Verificar que la carpeta contiene archivos antes de montarla
if os.path.isdir(DATA_DIR) and os.listdir(DATA_DIR):
    app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")
else:
    print("⚠️ Advertencia: La carpeta de datos está vacía o no existe.")

# 🔹 Incluir rutas del Backend si existen
if bathymetry_router:
    app.include_router(bathymetry_router, prefix="/bathymetry", tags=["Batimetría"])
else:
    print("⚠️ Advertencia: No se pudo cargar 'bathymetry_router'.")

if tiles_router:
    app.include_router(tiles_router, prefix="/tiles", tags=["Tiles"])
else:
    print("⚠️ Advertencia: No se pudo cargar 'tiles_router'.")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Batimetría"}
