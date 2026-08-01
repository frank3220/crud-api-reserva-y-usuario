from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from models.consumo import Consumo
from models.inventario import Inventario
from models.kardex_inventario import KardexInventario
from models.arqueo import ArqueoTurno  # 👈 IMPORTANTE: Importar el modelo de Arqueo

class ConsumoService:
    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # Crear consumo (Habitación o Patio)
    # ==========================
    def crear(self, data):
        try:
            # 1. 🔥 BUSCAR EL TURNO ACTIVO
            # Necesitamos el ID para que aparezca en el dashboard de una vez
            turno = (
                self.db.query(ArqueoTurno)
                .filter(ArqueoTurno.fecha_fin == None)
                .order_by(ArqueoTurno.id_arqueo.desc())
                .first()
            )

            if not turno:
                raise Exception("No hay un turno de arqueo activo para registrar consumos.")

            # 2. CREAR EL OBJETO CONSUMO
            consumo = Consumo(
                fecha=data.fecha,
                concepto=data.concepto,
                cantidad=data.cantidad,
                valor=data.valor,
                nota=data.nota,
                id_ocupacion=getattr(data, "id_ocupacion", None),
                id_producto=getattr(data, "id_producto", None),
                # 🔥 CAMBIO CLAVE: Asignamos el ID del arqueo encontrado
                id_arqueo=turno.id_arqueo  
            )

            self.db.add(consumo)
            self.db.flush()  # Para obtener el id_consumo para el Kardex

            # -----------------------------
            # Descontar inventario (SI ES PRODUCTO)
            # -----------------------------
            if consumo.id_producto:
                inv = (
                    self.db.query(Inventario)
                    .filter(Inventario.id_producto == consumo.id_producto)
                    .first()
                )

                if not inv:
                    raise Exception("Producto no existe en inventario")

                cantidad = int(consumo.cantidad or 1)
                stock_anterior = int(inv.stock or 0)

                if stock_anterior < cantidad:
                    raise Exception(f"Stock insuficiente. Disponible: {stock_anterior}")

                # Descontar stock
                inv.stock = stock_anterior - cantidad

                # Registrar KARDEX
                kardex = KardexInventario(
                    id_producto=consumo.id_producto,
                    fecha=datetime.now(),
                    tipo_movimiento="SALIDA",
                    cantidad=cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=inv.stock,
                    referencia=f"CONSUMO #{consumo.id_consumo}",
                )

                self.db.add(kardex)

            self.db.commit()
            self.db.refresh(consumo)
            return consumo

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error SQL: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise Exception(str(e))

    # ... (El resto de funciones listar y eliminar se mantienen igual)

    # ==========================
    # Listar consumos por ocupación
    # ==========================
    def listar_por_ocupacion(self, id_ocupacion: int):
        return (
            self.db.query(Consumo)
            .filter(Consumo.id_ocupacion == id_ocupacion)
            .order_by(Consumo.id_consumo.desc())
            .all()
        )
    

    # ==========================
    # 🔥 ELIMINAR CONSUMO (DEVUELVE STOCK)
    # ==========================
    def eliminar(self, id_consumo: int):
        try:
            consumo = self.db.get(Consumo, id_consumo)
            if not consumo:
                return False

            # devolver inventario si fue producto
            if consumo.id_producto:
                inv = (
                    self.db.query(Inventario)
                    .filter(Inventario.id_producto == consumo.id_producto)
                    .first()
                )

                if inv:
                    stock_anterior = int(inv.stock or 0)
                    inv.stock = stock_anterior + int(consumo.cantidad or 1)

                    kardex = KardexInventario(
                        id_producto=consumo.id_producto,
                        fecha=datetime.now(),
                        tipo_movimiento="ENTRADA",
                        cantidad=consumo.cantidad,
                        stock_anterior=stock_anterior,
                        stock_nuevo=inv.stock,
                        referencia=f"ELIMINA CONSUMO #{consumo.id_consumo}",
                    )
                    self.db.add(kardex)

            self.db.delete(consumo)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise Exception(str(e))
