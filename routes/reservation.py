from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session

# **CORRECCIÓN CRÍTICA:** Importar la función get_db REAL del archivo dependencies/database.py
from dependencies.database import get_db

# Importa los esquemas (modelos Pydantic)
from schemas.reservation import ReservationCreate, ReservationUpdate, Reservation as ReservationSchema

# Importa el servicio
from services.reservation import ReservationService


router = APIRouter(
    prefix="/reservas", # <--- ¡CAMBIADO de /reservations a /reservas!
    tags=["Reservations"]
)

# 1. CREATE (POST)
@router.post(
    "/", 
    response_model=ReservationSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva reserva"
)
def create_reservation_route(
    reservation_in: ReservationCreate, 
    db: Session = Depends(get_db)
):
    service = ReservationService(db)
    return service.create_reservation(reservation_in)


# 2. READ ALL (GET) - ¡Funcionalidad agregada!
@router.get(
    "/", 
    response_model=List[ReservationSchema],
    summary="Obtener todas las reservas"
)
def get_all_reservations_route(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    service = ReservationService(db)
    return service.get_all_reservations(skip=skip, limit=limit)


# 3. READ ONE (GET by ID) - ¡Funcionalidad agregada!
@router.get(
    "/{idreserva}", 
    response_model=ReservationSchema,
    summary="Obtener una reserva por su ID"
)
def get_reservation_by_id_route(
    idreserva: int, 
    db: Session = Depends(get_db)
):
    service = ReservationService(db)
    return service.get_reservation_by_id(idreserva)


# 4. UPDATE (PATCH) - Pendiente de implementar lógica en Repositorio
@router.patch(
    "/{idreserva}", 
    response_model=ReservationSchema,
    summary="Actualizar parcialmente una reserva"
)
def update_reservation_route(
    idreserva: int, 
    reservation_in: ReservationUpdate, 
    db: Session = Depends(get_db)
):
    service = ReservationService(db)
    return service.update_reservation(idreserva, reservation_in)


# 5. DELETE (DELETE) - Pendiente de implementar lógica en Repositorio
@router.delete(
    "/{idreserva}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una reserva"
)
def delete_reservation_route(
    idreserva: int, 
    db: Session = Depends(get_db)
):
    service = ReservationService(db)
    service.delete_reservation(idreserva)
    return {"message": "Reserva eliminada exitosamente."}