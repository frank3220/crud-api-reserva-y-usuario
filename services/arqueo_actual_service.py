from sqlalchemy.orm import Session
from models.arqueo_actual import ArqueoActual
from models.tsventas import tsventas  # Importamos para el amarre
from models.gastos import Gasto        # Importamos para el amarre
from models.acpm import AcpmLog       # Importamos para el amarre
from datetime import datetime, timedelta, timezone

COLOMBIA_TZ = timezone(timedelta(hours=-5))

class ArqueoActualService:

    def __init__(self, db: Session):
        self.db = db

    def get_actual(self) -> ArqueoActual:
        actual = self.db.query(ArqueoActual).first()
        if not actual:
            actual = ArqueoActual(
                consecutivo=1,
                fecha_inicio=datetime.now(COLOMBIA_TZ),
                total_ventas=0,
                total_acpm=0,
                total_gastos=0,
                neto=0,
            )
            self.db.add(actual)
            self.db.commit()
            self.db.refresh(actual)
        return actual

    def sumar_venta(self, valor: float):
        actual = self.get_actual()
        actual.total_ventas += float(valor)
        actual.neto = actual.total_ventas - actual.total_acpm - actual.total_gastos
        
        # ✅ AUTOMATIZACIÓN: Marcamos las ventas sueltas con el consecutivo actual
        self.db.query(tsventas).filter(tsventas.id_arqueo == None).update({"id_arqueo": actual.consecutivo})

        self.db.commit()
        return actual

    def sumar_acpm(self, valor: float):
        actual = self.get_actual()
        actual.total_acpm += float(valor)
        actual.neto = actual.total_ventas - actual.total_acpm - actual.total_gastos
        
        # ✅ AUTOMATIZACIÓN: Marcamos los registros de ACPM
        self.db.query(AcpmLog).filter(AcpmLog.id_arqueo == None).update({"id_arqueo": actual.consecutivo})

        self.db.commit()
        return actual

    def sumar_gasto(self, valor: float):
        actual = self.get_actual()
        actual.total_gastos += float(valor)
        actual.neto = actual.total_ventas - actual.total_acpm - actual.total_gastos
        
        # ✅ AUTOMATIZACIÓN: Marcamos los gastos
        self.db.query(Gasto).filter(Gasto.id_arqueo == None).update({"id_arqueo": actual.consecutivo})

        self.db.commit()
        return actual

    def cerrar_turno(self):
        actual = self.get_actual()

        # Antes de reiniciar, nos aseguramos de que TODO lo que quedó 
        # pendiente del día se amarre a este consecutivo final.
        self.db.query(tsventas).filter(tsventas.id_arqueo == None).update({"id_arqueo": actual.consecutivo})
        self.db.query(Gasto).filter(Gasto.id_arqueo == None).update({"id_arqueo": actual.consecutivo})
        self.db.query(AcpmLog).filter(AcpmLog.id_arqueo == None).update({"id_arqueo": actual.consecutivo})
        
        self.db.commit()

        datos = {
            "consecutivo": actual.consecutivo,
            "total_ventas": actual.total_ventas,
            "total_acpm": actual.total_acpm,
            "total_gastos": actual.total_gastos,
            "neto": actual.neto,
            "fecha_inicio": actual.fecha_inicio,
        }

        # Reiniciar para el nuevo turno
        actual.consecutivo += 1
        actual.fecha_inicio = datetime.now(COLOMBIA_TZ)
        actual.total_ventas = 0
        actual.total_acpm = 0
        actual.total_gastos = 0
        actual.neto = 0

        self.db.commit()
        return datos