from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas.room_type import RoomTypeCreate, RoomTypeOut
from services.room_type import RoomTypeService

# Inicializar el router con un prefijo y tag descriptivo
router = APIRouter(
    prefix="/room-types",
    tags=["Room Types | Tarifas"]
)

@router.get(
    "/", 
    response_model=list[RoomTypeOut], 
    summary="Obtener todos los Tipos de Habitación y Tarifas"
)
def read_room_types(db: Session = Depends(get_db)):
    """
    Retorna la lista de todos los tipos de habitación y sus tarifas horarias.
    """
    return RoomTypeService(db).get_all_types()

@router.post(
    "/", 
    response_model=RoomTypeOut, 
    status_code=status.HTTP_201_CREATED, 
    summary="Crear un nuevo Tipo de Habitación/Tarifa"
)
def create_room_type(type_data: RoomTypeCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo tipo de habitación con su tarifa por hora asociada.
    """
    return RoomTypeService(db).create_room_type(type_data)

@router.patch(
    "/{type_id}", 
    response_model=RoomTypeOut, 
    summary="Actualizar Tipo de Habitación/Tarifa por ID"
)
def update_room_type(type_id: int, type_data: RoomTypeCreate, db: Session = Depends(get_db)):
    """
    Actualiza el nombre, la tarifa o la descripción de un tipo de habitación existente.
    """
    return RoomTypeService(db).update_room_type(type_id, type_data)