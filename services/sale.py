from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List

import math # Necesario para la función ceil
from repositories.sale import SaleRepository
from schemas.sale import SaleCreate, SaleOut, SaleUpdate

class SaleService:
    def __init__(self, db: Session):
        self.repository = SaleRepository(db)

    def _calculate_total_cost(self, entry_time: datetime, exit_time: datetime, room_price_2h: float, room_price_add_hour: float) -> float:
        """
        Calcula el costo total basado en la duración de la estancia.
        Reglas:
        1. Estancia <= 2 horas (120 min) = Precio Fijo de 2h.
        2. Estancia > 2 horas: Precio Fijo + (Horas Adicionales REDONDEADAS HACIA ARRIBA) * Precio Hora Adicional.
        """
        # Calcular la duración total en minutos
        duration: timedelta = exit_time - entry_time
        total_minutes = duration.total_seconds() / 60
        
        # 1. Caso base: Menos o igual a 2 horas (120 minutos)
        if total_minutes <= 120:
            return room_price_2h

        # 2. Caso: Más de 2 horas
        cost = room_price_2h
        
        # Minutos adicionales después de las 2 horas base
        additional_minutes = total_minutes - 120
        
        # Convertir minutos adicionales a horas, redondeando HACIA ARRIBA
        # 121 min -> 1 hora adicional
        # 180 min (3h total) -> 1 hora adicional
        # 181 min (3h 1 min) -> 2 horas adicionales
        additional_hours = math.ceil(additional_minutes / 60)
        
        cost += additional_hours * room_price_add_hour
        
        return cost

    def create_sale(self, sale_data: SaleCreate) -> SaleOut:
        """Inicia una nueva venta al ocupar una habitación."""
        db_sale = self.repository.create_sale(sale_data)
        return SaleOut.model_validate(db_sale)

    def get_active_sales(self) -> List[SaleOut]:
        """Obtiene todas las ventas activas con detalles de la habitación."""
        sales = self.repository.get_active_sales()
        return [SaleOut.model_validate(sale) for sale in sales]

    def get_sale_by_id(self, sale_id: int) -> SaleOut:
        """Obtiene una venta por su ID."""
        sale = self.repository.get_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {sale_id} no encontrada."
            )
        return SaleOut.model_validate(sale)

    def finalize_sale(self, sale_id: int) -> SaleOut:
        """
        Calcula el costo final de la estancia y finaliza la venta.
        """
        # 1. Obtener la venta (debe incluir los datos de la habitación por joinedload)
        sale = self.repository.get_sale_by_id(sale_id)
        
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venta ID {sale_id} no encontrada.")
        
        if sale.estado != "ACTIVA":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La venta no está ACTIVA.")

        # 2. Definir la hora de salida y calcular el costo
        exit_time = datetime.now()
        
        # La relación 'habitacion' fue cargada en el repositorio
        room = sale.habitacion 
        
        total_cost = self._calculate_total_cost(
            entry_time=sale.fecha_entrada,
            exit_time=exit_time,
            room_price_2h=room.precio_2h,
            room_price_add_hour=room.precio_hora_adicional
        )
        
        # 3. Preparar datos para actualizar la venta
        update_data = {
            "fecha_salida": exit_time,
            "monto_total": total_cost,
            "estado": "FINALIZADA"
        }
        
        # 4. Actualizar la venta en la base de datos
        final_sale_db = self.repository.update_sale(sale_id, update_data)
        
        if not final_sale_db:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al guardar la finalización de la venta.")
             
        return SaleOut.model_validate(final_sale_db)