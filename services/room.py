# services/room.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from sqlalchemy import func

from models.room import tshabitacion
from models.ocupacion import Ocupacion
from models.consumo import Consumo
from repositories.room import RoomRepository
from schemas.room import RoomCreate, RoomUpdate, RoomOut, RoomFullOut


class RoomService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = RoomRepository(db)

    # ------------------------------------------------------
    # CREAR HABITACIÓN
    # ------------------------------------------------------
    def create_room(self, room_data: RoomCreate) -> RoomOut:
        existing_room = self.repository.get_room_by_number(room_data.numhabitacion)
        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El número de habitación {room_data.numhabitacion} ya existe."
            )

        db_room = self.repository.create_room(room_data)
        return RoomOut.model_validate(db_room)

    # ------------------------------------------------------
    # OBTENER TODAS LAS HABITACIONES (CON CONSUMOS)
    # ------------------------------------------------------
    def get_all_rooms(self) -> List[RoomFullOut]:
        rooms = self.repository.get_all_rooms()
        result: List[RoomFullOut] = []

        for room in rooms:
            ocupacion = (
                self.db.query(Ocupacion)
                .filter(
                    Ocupacion.id_habitacion == room.id_habitacion,
                    Ocupacion.hora_salida.is_(None)
                )
                .first()
            )

            total_consumos = 0

            if ocupacion:
                total_consumos = (
                    self.db.query(
                        func.coalesce(
                            func.sum(Consumo.valor * Consumo.cantidad), 0
                        )
                    )
                    .filter(
                        Consumo.id_ocupacion == ocupacion.id_ocupacion,
                        Consumo.id_arqueo.is_(None)
                    )
                    .scalar()
                )

            data = {
                "id_habitacion": room.id_habitacion,
                "numhabitacion": room.numhabitacion,
                "nombre": room.nombre,
                "tipo": room.tipo,
                "capacidad": room.capacidad,
                "precio_2h": room.precio_2h,
                "precio_hora_adicional": room.precio_hora_adicional,
                "estado": room.estado,
                "descripcion": room.descripcion,
                "activa": room.activa,

                # 🔥 EXTRA PARA FRONTEND
                "status": "ocupada" if ocupacion else "disponible",
                "entrada": ocupacion.hora_entrada if ocupacion else None,
                "id_ocupacion": ocupacion.id_ocupacion if ocupacion else None,
                "total_consumos": float(total_consumos),
            }

            result.append(RoomFullOut(**data))

        return result

# ------------------------------------------------------
    # OBTENER UNA HABITACIÓN POR ID
    # ------------------------------------------------------
    def get_room(self, room_id: int) -> RoomOut:
        room = self.repository.get_room_by_id(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Habitación con ID {room_id} no encontrada."
            )
        return RoomOut.model_validate(room)

    # ------------------------------------------------------
    # 🔥 CAMBIAR ESTADO DE HABITACIÓN (La que faltaba)
    # ------------------------------------------------------
    def change_room_status(self, room_id: int, nuevo_estado: str) -> RoomOut:
        room = self.db.query(tshabitacion).filter(tshabitacion.id_habitacion == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Habitación no encontrada"
            )
        
        # Actualizamos el estado (ej: 'disponible', 'limpieza', 'mantenimiento')
        room.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(room)
        
        return RoomOut.model_validate(room)

    # ------------------------------------------------------
    # ACTUALIZAR DATOS DE LA HABITACIÓN
    # ------------------------------------------------------
    # --- services/room.py ---
    def update_room(self, room_id: int, room_data: RoomUpdate) -> RoomOut:
        db_room = self.repository.get_room_by_id(room_id)
        if not db_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada."
            )
        
        # 🌟 CORRECCIÓN QUIRÚRGICA: Le pasamos el room_id tal como lo espera tu repositorio
        updated_room = self.repository.update_room(room_id, room_data)
        return RoomOut.model_validate(updated_room)