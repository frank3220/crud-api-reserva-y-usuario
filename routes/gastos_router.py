# routes/gastos.py

# routes/gastos.py

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from dependencies.database import get_db
from services.gastos_service import GastosService
from schemas.gastos_schema import GastoCreate
# 👈 IMPORTANTE: Importa tu función de turno activo aquí
from routes.dashboard import asegurar_turno_activo 

# Zona horaria Colombia
COLOMBIA_TZ = timezone(timedelta(hours=-5))

router = APIRouter(prefix="/gastos", tags=["Gastos"])

def fecha_colombia_hoy():
    return datetime.now(COLOMBIA_TZ).date()

# ============================================================
# 🟢 CREAR GASTO (CONTADO / CREDITO)
# ============================================================
@router.post("/", summary="Registrar un gasto")
def crear_gasto(data: GastoCreate, db: Session = Depends(get_db)):
    # 1. Obtener el turno que está abierto actualmente
    # Esto asegura que el gasto quede "amarrado" al arqueo de hoy
    turno_actual = asegurar_turno_activo(db)
    
    # 2. Forzar fecha y asignar el ID del arqueo
    data.fecha = fecha_colombia_hoy()
    data.id_arqueo = turno_actual.id_arqueo # 👈 CLAVE: Asignamos el ID del turno activo

    svc = GastosService(db)
    
    # El servicio 'svc.crear' ahora recibirá el objeto con el id_arqueo lleno
    return svc.crear(data)

# ... el resto de tus rutas (listar_gastos_dia, listar_todos, etc.)

# ============================================================
# 🟢 LISTAR GASTOS POR DÍA
# ============================================================
@router.get("/dia", summary="Listar gastos de un día")
def listar_gastos_dia(fecha: str, db: Session = Depends(get_db)):
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Formato de fecha incorrecto. Use YYYY-MM-DD")

    svc = GastosService(db)
    return svc.listar_dia(fecha_obj)


# ============================================================
# 🟢 LISTAR TODOS LOS GASTOS
# ============================================================
@router.get("/", summary="Listar todos los gastos")
def listar_todos(db: Session = Depends(get_db)):
    svc = GastosService(db)
    return svc.listar_todos()


# ============================================================
# 🟡 LISTAR GASTOS PENDIENTES (sin asignar a un arqueo)
# ============================================================
@router.get("/pendientes", summary="Listar gastos no asignados a un arqueo")
def listar_pendientes(db: Session = Depends(get_db)):
    svc = GastosService(db)
    return svc.listar_pendientes()


# ============================================================
# 🔴 ASIGNAR GASTOS AL ARQUEO
# ============================================================
@router.post("/asignar-arqueo/{id_arqueo}", summary="Asignar gastos al arqueo")
def asignar_gastos(id_arqueo: int, db: Session = Depends(get_db)):
    svc = GastosService(db)
    return svc.asignar_a_arqueo(id_arqueo)
