from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

# DB
from dependencies.database import get_db

# Services
from services.room import RoomService
from services.config_service import ConfigService

# Models
from models.room import tshabitacion
from models.ocupacion import Ocupacion

# Schemas
from schemas.room import RoomCreate, RoomUpdate, RoomOut

# 🔥 SEGURIDAD: Importamos las nuevas herramientas
from utils.security import get_current_user, RoleChecker

router = APIRouter(
    prefix="/rooms",
    tags=["Habitaciones"],
    responses={404: {"description": "No encontrado"}},
)

# ============================================================
# FUNCIÓN INTERNA → AUTO-LIMPIEZA
# ============================================================
def procesar_auto_limpieza(db: Session, room: tshabitacion):
    if room.estado != "LIMPIEZA" or not room.hora_limpiar:
        return
    ahora = datetime.now()
    if ahora >= room.hora_limpiar:
        room.estado = "DISPONIBLE"
        room.hora_limpiar = None
        db.commit()
        db.refresh(room)

# ============================================================
# 1. CREAR HABITACIÓN (🔒 SOLO ADMIN)
# ============================================================
@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room_route(
    room_data: RoomCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["ADMIN"])) # Solo Admin crea
):
    room_service = RoomService(db)
    return room_service.create_room(room_data)

# ============================================================
# 2. READ ALL (🔑 CUALQUIER USUARIO LOGUEADO)
# ============================================================
# ============================================================
# 2. READ ALL (🔑 CUALQUIER USUARIO LOGUEADO)
# ============================================================
@router.get("/", response_model=list)
def get_all_rooms_route(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Requiere estar logueado
):
    config = ConfigService(db)
    minutos_gracia = config.get("minutos_gracia", 8)

    rooms = db.query(tshabitacion).all()
    resultado = []

    for r in rooms:
        procesar_auto_limpieza(db, r)
        ocup = (
            db.query(Ocupacion)
            .filter(
                Ocupacion.id_habitacion == r.id_habitacion,
                Ocupacion.hora_salida.is_(None),
            )
            .first()
        )

        estado = r.estado
        entrada = ocup.hora_entrada if ocup else None
        id_ocup = ocup.id_ocupacion if ocup else None
        tiempo_min = 0
        cobrar_hora_extra = False

        if entrada:
            diff = datetime.now() - entrada
            tiempo_min = int(diff.total_seconds() // 60)
            if tiempo_min > (120 + minutos_gracia):
                cobrar_hora_extra = True

        # 🌟 CONTROL DE COLORES E IDENTIFICACIÓN DE AMANECIDAS
        # 🌟 CONTROL DE COLORES INTELIGENTE (BASADO EN LA OCUPACIÓN REAL)
        es_amanecida_real = False
        if ocup:
            # Si la ocupación tiene la palabra amanecida o el estado de la hab es "A"
            es_amanecida_real = (estado == "A") or "amanecida" in (ocup.observaciones or "").lower()

        if estado == "LIMPIEZA":
            estado_color = "purple"
        elif es_amanecida_real:
            estado_color = "orange"  # Fuerza el color naranja de amanecida en el Front
            estado = "A"             # Sincroniza el estado para el Front
        elif estado == "OCUPADA" or ocup:
            estado_color = "red"
            if cobrar_hora_extra:
                estado_color = "yellow"
        else:
            estado_color = "blue"

        # Extraemos el valor real guardado en la ocupación
        # Si es amanecida, usamos el total_pagar de la ocupación. Si no, dejamos que el front use el precio base
        monto_ocupacion = float(ocup.total_pagar) if (ocup and ocup.total_pagar is not None) else None
        if es_amanecida_real and (monto_ocupacion is None or monto_ocupacion == 0):
            # Si por algún motivo falló el guardado, usamos el precio_2h de la habitación como salvavidas
            monto_ocupacion = float(r.precio_2h) if r.precio_2h else 0.0

        resultado.append({
            "id_habitacion": r.id_habitacion,
            "numhabitacion": r.numhabitacion,
            "nombre": r.nombre,
            "tipo": r.tipo,
            "capacidad": r.capacidad,
            "precio_2h": r.precio_2h,
            "precio_hora_adicional": r.precio_hora_adicional,
            "estado": estado,
            "estado_color": estado_color,
            "entrada": entrada,
            "tiempo_minutos": tiempo_min,
            "hora_extra": cobrar_hora_extra,
            "id_ocupacion": id_ocup,
            "hora_limpiar": r.hora_limpiar,
            "activa": r.activa,
            # 🌟 CLAVE: Le enviamos a React el monto guardado en la DB para que no use los $25.000 por defecto
            "total_pagar": monto_ocupacion 
        })
    return resultado

# ============================================================
# 3. READ AVAILABLE (🔑 CUALQUIER USUARIO)
# ============================================================
@router.get("/available", response_model=list)
def get_available_rooms_route(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Si no tienes get_available_rooms en el service, esta es la forma segura:
    rooms = db.query(tshabitacion).filter(tshabitacion.estado == "DISPONIBLE", tshabitacion.activa == True).all()
    return rooms
# ============================================================
# 5. UPDATE (🔒 SOLO ADMIN)
# ============================================================
@router.put("/{room_id}", response_model=RoomOut)
def update_room_route(
    room_id: int, 
    room_data: RoomUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["ADMIN"])) # Solo Admin edita
):
    room_service = RoomService(db)
    return room_service.update_room(room_id, room_data)

# ============================================================
# 6. DELETE (🔒 SOLO ADMIN)
# ============================================================
@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_route(
    room_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["ADMIN"])) # Solo Admin borra
):
    room_service = RoomService(db)
    room_service.delete_room(room_id)
    return

# ============================================================
# 7. CAMBIAR ESTADO MANUAL (🔑 CAJERO O ADMIN)
# ============================================================
@router.patch("/{room_id}/status", response_model=RoomOut)
def change_room_status_route(
    room_id: int,
    status_update: dict, # El front debe mandar {"estado": "LIMPIEZA"}
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    nuevo_estado = status_update.get("estado")
    if not nuevo_estado:
        raise HTTPException(status_code=400, detail="El campo 'estado' es obligatorio")

    # Aquí es donde fallaba antes porque no existía la función en el Service
    room_service = RoomService(db)
    return room_service.change_room_status(room_id, nuevo_estado.upper())