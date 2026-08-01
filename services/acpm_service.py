from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.acpm import AcpmLog
from models.arqueo import ArqueoTurno
from schemas.acpm import ACPMCreate


class AcpmService:
    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # 🟩 REGISTRAR ACPM (PENDIENTE, SE ASIGNA AL CERRAR TURNO)
    # ============================================================
    def registrar(self, data: ACPMCreate):
        # 1. Buscamos el turno activo
        turno = (
            self.db.query(ArqueoTurno)
            .filter(ArqueoTurno.fecha_fin == None)
            .order_by(ArqueoTurno.id_arqueo.desc())
            .first()
        )

        if not turno:
            raise HTTPException(400, "No hay turno activo para registrar ACPM")

        fecha_acpm = getattr(data, "fecha", None)
        if not fecha_acpm:
            fecha_acpm = turno.fecha_inicio.date()

        saldo = data.valor_total if data.tipo_pago == "credito" else 0

        nuevo = AcpmLog(
            fecha=fecha_acpm,
            litros=data.litros,
            valor_total=data.valor_total,
            proveedor=data.proveedor,
            nota=data.nota,
            tipo_pago=data.tipo_pago,
            saldo_pendiente=saldo,
            pagado=1 if data.tipo_pago == "contado" else 0,
            fecha_pago=fecha_acpm if data.tipo_pago == "contado" else None,
            # ✅ CAMBIO CLAVE: Ya no es None, le asignamos el ID del turno de una vez
            id_arqueo=turno.id_arqueo,  
        )

        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)

        return nuevo