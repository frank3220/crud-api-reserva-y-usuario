from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from utils.settings import CORS_ORIGINS

from dependencies.database import Base, engine
from models.arqueo import ArqueoTurno 
from models.acpm import AcpmLog


from routes import inventario
from routes import auth

# Routers (Importaciones)
from routes import room as room_router
from routes import usuario as usuario_router
from routes import reservation as reservation_router
from routes import operation as operation_router
from routes import room_type as room_type_router
from routes import reset_password
from routes.ocupacion import router as ocupacion_router
from routes.acpm_router import router as acpm_router
from routes.dashboard import router as dashboard_router
from routes.gastos_router import router as gastos_router
from routes.consumos import router as consumos_router
from routes import productos, proveedores
from routes.compras_proveedor import router as compras_proveedor_router

app = FastAPI(
    title="IAMOTELFASTAPI",
    description="API Motel Donde MamÃ¡ - GestiÃ³n con Roles y Arqueo",
    version="1.1.0",
)

# ðŸ”¥ CORS â€” Corregido para aceptar cualquier puerto local si cambias
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Rutas de la API
# 1. AutenticaciÃ³n (Login)
app.include_router(auth.router) # Esto maneja /auth/login

# 2. Usuarios y Perfiles 
# QUITAMOS el prefijo aquÃ­ porque ya lo pusimos dentro del router/usuario.py
app.include_router(usuario_router.router) 
app.include_router(reset_password.router)

# 3. OperaciÃ³n Principal e Inventarios
app.include_router(room_router.router)
app.include_router(room_type_router.router)
app.include_router(ocupacion_router)
app.include_router(reservation_router.router)
app.include_router(productos.router)
app.include_router(proveedores.router)
app.include_router(compras_proveedor_router)
app.include_router(inventario.router)

# 4. AdministraciÃ³n y Finanzas
app.include_router(dashboard_router)
app.include_router(operation_router.router_dashboard)
app.include_router(acpm_router)
app.include_router(gastos_router)
app.include_router(consumos_router)

# Archivos estÃ¡ticos al final para no interferir con las rutas de la API
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, "public")):
    app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "public")), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    index = os.path.join(BASE_DIR, "public", "index.html")
    if not os.path.exists(index):
        return HTMLResponse("<h1>Servidor API Online</h1>", status_code=200)
    return FileResponse(index)

    # ... (lo que ya tienes arriba)

