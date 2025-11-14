from sqlalchemy.orm import Session
from models.reservation import ReservationModel 
from schemas.reservation import ReservationCreate
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, reservation_in: ReservationCreate) -> ReservationModel:
        """Crea una nueva reserva."""
        
        db_reservation = ReservationModel(
            keyreserva=reservation_in.keyreserva,
            estado=reservation_in.estado,
            fecha=reservation_in.fecha,
            hora=reservation_in.hora,
            tiempo=reservation_in.tiempo,
            numhabitacion=reservation_in.numhabitacion,
            tipopago=reservation_in.tipopago,
            valor=reservation_in.valor,
            userid=reservation_in.userid
        )

        try:
            self.db.add(db_reservation)
            self.db.commit()
            self.db.refresh(db_reservation)
            return db_reservation
        
        except IntegrityError as e:
            self.db.rollback()
            
            # 1. Manejo del Error de Clave Foránea (userid inexistente)
            error_message = str(e)
            if "foreign key constraint fails" in error_message or "FOREIGN KEY constraint failed" in error_message:
                # Usamos el detalle original para que el cliente sepa qué ID falta
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error de Integridad: El ID de usuario ({reservation_in.userid}) no existe. Por favor, cree el usuario primero."
                )
            
            # 2. Error de Integridad general (ej. clave única duplicada, como keyreserva)
            # Intentamos obtener el detalle del error de la base de datos
            error_detail = e.orig.args[1] if e.orig and len(e.orig.args) > 1 else error_message
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad en la reserva: {error_detail}"
            )
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado al guardar la reserva: {e}"
            )

    # ******* MÉTODO AGREGADO PARA SOLUCIONAR EL AttributeError *******
    def get_by_key(self, keyreserva: str) -> ReservationModel | None:
        """Obtiene una reserva por su clave única 'keyreserva'."""
        return self.db.query(ReservationModel).filter(
            ReservationModel.keyreserva == keyreserva
        ).first()
    # *******************************************************************
    
    def get_all(self, skip: int = 0, limit: int = 100):
        """Obtiene todas las reservas con paginación."""
        return self.db.query(ReservationModel).offset(skip).limit(limit).all()