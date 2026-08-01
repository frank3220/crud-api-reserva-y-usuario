from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

# CLAVE: Importamos el nombre de clase CORREGIDO 'tshabitacion'
from models.room import tshabitacion 
from schemas.room import RoomCreate, RoomUpdate, RoomOut

class RoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_room(self, room_data: RoomCreate) -> tshabitacion:
        # Crea la instancia del modelo usando 'tshabitacion'
        db_room = tshabitacion(**room_data.model_dump())
        self.db.add(db_room)
        self.db.commit()
        self.db.refresh(db_room)
        return db_room

    def get_all_rooms(self) -> List[tshabitacion]:
        # Consulta la tabla usando 'tshabitacion'
        stmt = select(tshabitacion)
        return self.db.execute(stmt).scalars().all()

    def get_room_by_id(self, room_id: int) -> Optional[tshabitacion]:
        # Busca por ID usando 'tshabitacion'
        return self.db.get(tshabitacion, room_id)

    def get_room_by_number(self, numhabitacion: str) -> Optional[tshabitacion]:
        # Busca por número usando 'tshabitacion'
        stmt = select(tshabitacion).where(tshabitacion.numhabitacion == numhabitacion)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_available_rooms(self) -> List[tshabitacion]:
        # Busca habitaciones disponibles y activas
        stmt = select(tshabitacion).where(
            tshabitacion.estado == "DISPONIBLE",
            tshabitacion.activa == True
        )
        return self.db.execute(stmt).scalars().all()

    def update_room(self, room_id: int, room_data: RoomUpdate) -> Optional[tshabitacion]:
        db_room = self.db.get(tshabitacion, room_id)
        if db_room:
            update_data = room_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_room, key, value)
            self.db.commit()
            self.db.refresh(db_room)
            return db_room
        return None

    def delete_room(self, room_id: int) -> bool:
        db_room = self.db.get(tshabitacion, room_id)
        if db_room:
            self.db.delete(db_room)
            self.db.commit()
            return True
        return False