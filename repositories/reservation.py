import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.reservation import ReservationModel
from schemas.reservation import ReservationCreate, ReservationUpdate


logger = logging.getLogger(__name__)


class ReservationRepository:
    def __init__(self, db: Session, company_id: int = 1, motel_id: int = 1):
        self.db = db
        self.company_id = company_id
        self.motel_id = motel_id

    def _tenant_filters(self):
        return (
            ReservationModel.id_company == self.company_id,
            ReservationModel.id_motel == self.motel_id,
        )

    def create(self, reservation_in: ReservationCreate) -> ReservationModel:
        db_reservation = ReservationModel(
            id_company=self.company_id,
            id_motel=self.motel_id,
            keyreserva=reservation_in.keyreserva,
            estado=reservation_in.estado,
            fecha=reservation_in.fecha,
            hora=reservation_in.hora,
            tiempo=reservation_in.tiempo,
            numhabitacion=reservation_in.numhabitacion,
            tipopago=reservation_in.tipopago,
            valor=reservation_in.valor,
            userid=reservation_in.userid,
        )

        try:
            self.db.add(db_reservation)
            self.db.commit()
            self.db.refresh(db_reservation)
            return db_reservation
        except IntegrityError as error:
            self.db.rollback()
            logger.exception("Error de integridad al guardar reserva.")
            error_message = str(error)
            if "foreign key constraint fails" in error_message or "FOREIGN KEY constraint failed" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario asociado a la reserva no existe.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo guardar la reserva por un conflicto de datos.",
            )
        except Exception:
            self.db.rollback()
            logger.exception("Error inesperado al guardar reserva.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al guardar la reserva.",
            )

    def get_by_key(self, keyreserva: str) -> ReservationModel | None:
        return self.db.query(ReservationModel).filter(
            *self._tenant_filters(),
            ReservationModel.keyreserva == keyreserva,
        ).first()

    def get_by_id(self, idreserva: int) -> ReservationModel | None:
        return self.db.query(ReservationModel).filter(
            *self._tenant_filters(),
            ReservationModel.idreserva == idreserva,
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ReservationModel]:
        return (
            self.db.query(ReservationModel)
            .filter(*self._tenant_filters())
            .order_by(ReservationModel.fecha.desc(), ReservationModel.hora.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_room_and_date(self, numhabitacion: str, fecha) -> list[ReservationModel]:
        return self.db.query(ReservationModel).filter(
            *self._tenant_filters(),
            ReservationModel.numhabitacion == numhabitacion,
            ReservationModel.fecha == fecha,
            ReservationModel.estado.notin_(["CANCELADA", "CANCELADO", "ANULADA", "ANULADO"]),
        ).all()

    def update(self, db_reservation: ReservationModel, reservation_in: ReservationUpdate) -> ReservationModel:
        update_data = reservation_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_reservation, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_reservation)
            return db_reservation
        except IntegrityError:
            self.db.rollback()
            logger.exception("Error de integridad al actualizar reserva.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar la reserva por un conflicto de datos.",
            )
        except Exception:
            self.db.rollback()
            logger.exception("Error inesperado al actualizar reserva.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al actualizar la reserva.",
            )

    def delete(self, db_reservation: ReservationModel) -> None:
        try:
            self.db.delete(db_reservation)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception("Error inesperado al eliminar reserva.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al eliminar la reserva.",
            )
