from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, and_
from typing import List, Optional

# Importamos los modelos de SQLAlchemy
from models.tsventas import tsventas
from models.room import tshabitacion
# Importamos los esquemas Pydantic
from schemas.sale import SaleCreate, SaleUpdate

class SaleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_sale(self, sale_data: SaleCreate) -> tsventas:
        """Crea un nuevo registro de venta (entrada de habitación)."""
        db_sale = tsventas(**sale_data.model_dump())
        self.db.add(db_sale)
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale

    def get_sale_by_id(self, sale_id: int) -> Optional[tsventas]:
        """Obtiene una venta por su ID, cargando la habitación relacionada."""
        # Usamos joinedload para cargar los datos de la habitación en la misma consulta
        stmt = select(tsventas).options(joinedload(tsventas.habitacion)).where(tsventas.id_venta == sale_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_sales(self) -> List[tsventas]:
        """Obtiene todas las ventas que están actualmente 'ACTIVA', cargando la habitación."""
        stmt = select(tsventas).options(joinedload(tsventas.habitacion)).where(tsventas.estado == "ACTIVA")
        return self.db.execute(stmt).scalars().all()

    def update_sale(self, sale_id: int, update_data: dict) -> Optional[tsventas]:
        """Actualiza campos específicos de una venta, utilizado para el check-out."""
        db_sale = self.db.get(tsventas, sale_id)
        if db_sale:
            for key, value in update_data.items():
                setattr(db_sale, key, value)
            self.db.commit()
            self.db.refresh(db_sale)
            return db_sale
        return None