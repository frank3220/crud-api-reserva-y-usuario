from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Importaciones de la configuración de la base de datos y modelos
from dependencies.database import Base, engine
# CLAVE: Importar los modelos asegura que SQLAlchemy los cargue en 
# la memoria antes de llamar a create_tables().
from models import reservation as reservation_models 
from models import usuario as usuario_models 

# Importa los routers
from routes import usuario
from routes import reservation as reservation_routes

# *****************************************************************
# 1. FUNCIÓN PARA CREAR TABLAS
# *****************************************************************
def create_tables():
    """Crea todas las tablas definidas en los modelos si no existen."""
    print("Intentando crear las tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas o creadas exitosamente.")

# *****************************************************************
# 2. INICIALIZACIÓN DE FASTAPI
# *****************************************************************
app = FastAPI(
    title="IAMOTELFASTAPI",
    description="API de gestión de reservas, habitaciones y usuarios para IAMOTEL.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# EJECUCIÓN CLAVE: Llama a la función para crear tablas al inicio
create_tables()

# *****************************************************************
# 3. INCLUSIÓN DE ROUTERS
# *****************************************************************
# Rutas de USUARIOS: Prefijo /api/v1 (monta en /api/v1/usuarios)
app.include_router(usuario.router, prefix="/api/v1") 

# Rutas de RESERVAS: Monta directamente, usando el prefijo interno /reservations
app.include_router(reservation_routes.router) 


# *****************************************************************
# 4. CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS Y RUTA RAÍZ
# *****************************************************************
INDEX_FILE = os.path.join("public", "index.html")

# Montar el Directorio Estático (permite acceder a CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="public"), name="static")

# Ruta Raíz para Servir la Página de Bienvenida (index.html)
@app.get("/", response_class=HTMLResponse, summary="Página de Bienvenida")
async def read_root():
    # Asegúrate de que el archivo exista antes de intentar servirlo
    if not os.path.exists(INDEX_FILE):
        return HTMLResponse(
            status_code=404, 
            content="<h1>Error 404: Archivo index.html no encontrado en la carpeta 'public'.</h1>"
        )
    # Retorna el archivo index.html
    return FileResponse(INDEX_FILE)