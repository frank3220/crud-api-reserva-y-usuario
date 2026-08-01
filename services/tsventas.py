from sqlalchemy.orm import Session, joinedload # Importamos joinedload para traer al usuario
from sqlalchemy import desc
from fastapi import HTTPException, status
from typing import List
from datetime import datetime

# Importamos tus modelos
from models.tsventas import tsventas 
from models.usuario import Usuario # Asegúrate de que el modelo se llame Usuarios o Usuario

class SaleService:
    """Clase de servicio para gestionar operaciones de ventas."""

    def __init__(self, db: Session):
        self.db = db

    def get_active_sales(self) -> List[tsventas]:
        """
        Obtiene todas las ventas 'ACTIVA' incluyendo el nombre del cajero.
        """
        try:
            # ✅ CAMBIO CLAVE: Usamos joinedload para traer la info del usuario 
            # vinculada por id_usuario_registro
            query = self.db.query(tsventas).options(
                joinedload(tsventas.usuario_relacion) # Esto asume que tienes la relación en el modelo
            ).filter(
                tsventas.tsestado == 'ACTIVA'
            ).order_by(desc(tsventas.tsfecha))
            
            return query.all()
        
        except Exception as e:
            print(f"Error en get_active_sales: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error al obtener ventas con cajero: {e}"
            )