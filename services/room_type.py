from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.room_type import RoomType
from schemas.room_type import RoomTypeCreate, RoomTypeOut

class RoomTypeService:
    """Clase de servicio para manejar la lógica de Tipos de Habitación y Tarifas."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_types(self):
        """Obtiene todos los tipos de habitación."""
        return self.db.query(RoomType).all()

    def get_type_by_id(self, type_id: int):
        """Obtiene un tipo de habitación por ID."""
        type_db = self.db.query(RoomType).filter(RoomType.id == type_id).first()
        if not type_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tipo de habitación no encontrado"
            )
        return type_db

    def create_room_type(self, type_data: RoomTypeCreate):
        """Crea un nuevo tipo de habitación con su tarifa."""
        # Verificar si el nombre ya existe
        existing_type = self.db.query(RoomType).filter(RoomType.nombre == type_data.nombre).first()
        if existing_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Ya existe un tipo de habitación con ese nombre"
            )

        db_room_type = RoomType(
            nombre=type_data.nombre,
            tarifa_por_hora=type_data.tarifa_por_hora,
            descripcion=type_data.descripcion
        )
        self.db.add(db_room_type)
        self.db.commit()
        self.db.refresh(db_room_type)
        return db_room_type

    def update_room_type(self, type_id: int, type_data: RoomTypeCreate):
        """Actualiza un tipo de habitación existente."""
        db_room_type = self.get_type_by_id(type_id)

        # Verificar si el nuevo nombre ya existe en otro registro
        if self.db.query(RoomType).filter(
            RoomType.nombre == type_data.nombre,
            RoomType.id != type_id
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Ya existe otro tipo de habitación con ese nombre"
            )

        db_room_type.nombre = type_data.nombre
        db_room_type.tarifa_por_hora = type_data.tarifa_por_hora
        db_room_type.descripcion = type_data.descripcion
        
        self.db.commit()
        self.db.refresh(db_room_type)
        return db_room_type