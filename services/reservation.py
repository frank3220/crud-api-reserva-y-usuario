from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from repositories.reservation import ReservationRepository
from schemas.reservation import ReservationCreate, ReservationUpdate, Reservation as ReservationSchema

class ReservationService:
    def __init__(self, db: Session):
        self.repo = ReservationRepository(db)

    # 1. CREATE
    def create_reservation(self, reservation_in: ReservationCreate) -> ReservationSchema:
        # Lógica de negocio: Verificar si la keyreserva ya existe
        existing_reservation = self.repo.get_by_key(keyreserva=reservation_in.keyreserva)
        if existing_reservation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La clave de reserva ya existe."
            )
        
        # TODO: Lógica de negocio adicional: Verificar disponibilidad de la habitación
        
        db_reservation = self.repo.create(reservation_in)
        return ReservationSchema.model_validate(db_reservation)

    # 2. READ ALL
    def get_all_reservations(self, skip: int = 0, limit: int = 100) -> List[ReservationSchema]:
        reservations = self.repo.get_all(skip=skip, limit=limit)
        return [ReservationSchema.model_validate(r) for r in reservations]

    # 3. READ ONE
    def get_reservation_by_id(self, idreserva: int) -> ReservationSchema:
        reservation = self.repo.get_by_id(idreserva)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {idreserva} no encontrada."
            )
        return ReservationSchema.model_validate(reservation)

    # 4. UPDATE
    def update_reservation(self, idreserva: int, reservation_in: ReservationUpdate) -> ReservationSchema:
        db_reservation = self.repo.get_by_id(idreserva)
        if not db_reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {idreserva} no encontrada."
            )
        
        # TODO: Lógica de negocio para cambios de estado, etc.

        updated_reservation = self.repo.update(db_reservation, reservation_in)
        return ReservationSchema.model_validate(updated_reservation)

    # 5. DELETE
    def delete_reservation(self, idreserva: int) -> None:
        db_reservation = self.repo.get_by_id(idreserva)
        if not db_reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {idreserva} no encontrada."
            )
        self.repo.delete(db_reservation)