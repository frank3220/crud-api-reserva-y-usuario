from models.gastos import Gasto
from models.proveedor import Proveedor  # 🔥 IMPORTANTE: Importar el modelo
from sqlalchemy.orm import Session
from datetime import date

from models.arqueo import ArqueoTurno


class GastosService:
    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # 🟢 CREAR GASTO (CONEXIÓN CON PROVEEDOR CORREGIDA)
    # ============================================================
    def crear(self, data):
        # 1. Obtener turno activo
        turno = (
            self.db.query(ArqueoTurno)
            .filter(ArqueoTurno.fecha_fin == None)
            .order_by(ArqueoTurno.id_arqueo.desc())
            .first()
        )

        if not turno:
            raise Exception("No hay turno activo")

        # 2. Manejo de fecha
        fecha_gasto = getattr(data, "fecha", None) or turno.fecha_inicio.date()

        # 3. EXTRACCIÓN FORZADA DE CANTIDAD
        # Intentamos sacarlo como atributo o como diccionario
        if hasattr(data, 'cantidad'):
            cant_final = data.cantidad
        elif isinstance(data, dict):
            cant_final = data.get('cantidad', 1)
        else:
            cant_final = 1
            
        # Si llega como None o 0, forzamos a 1
        if not cant_final:
            cant_final = 1

        gasto = Gasto(
            fecha=fecha_gasto,
            concepto=data.concepto,
            valor=data.valor,
            cantidad=cant_final,  # <--- USAMOS LA VARIABLE YA VALIDADA
            id_proveedor=getattr(data, "id_proveedor", None), 
            proveedor=getattr(data, "proveedor", None),
            nota=getattr(data, "nota", None),
            tipo_pago=data.tipo_pago,
            id_arqueo=turno.id_arqueo
        )

        self.db.add(gasto)
        self.db.commit()
        self.db.refresh(gasto)

        return gasto

    # ============================================================
    # 🟢 LISTAR GASTOS POR FECHA (CON JOIN PARA EL NOMBRE)
    # ============================================================
    def listar_dia(self, fecha: date):
        # 🔥 CAMBIO CLAVE: Usamos query(Gasto, Proveedor) y join() 
        # para que el frontend reciba el nombre del proveedor
        resultados = (
            self.db.query(
                Gasto, 
                Proveedor.nombre.label("nombre_proveedor")
            )
            .join(Proveedor, Gasto.id_proveedor == Proveedor.id_proveedor, isouter=True)
            .filter(Gasto.fecha == fecha)
            .order_by(Gasto.id_gasto.desc())
            .all()
        )

        lista_final = []
        for gasto, nombre_prov in resultados:
            gasto_dict = {
                "id_gasto": gasto.id_gasto,
                "fecha": gasto.fecha,
                "concepto": gasto.concepto,
                "valor": gasto.valor,
                "tipo_pago": gasto.tipo_pago,
                "nombre_proveedor": nombre_prov or gasto.proveedor,
                "id_arqueo": gasto.id_arqueo,
                # 🚀 CAMBIO QUIRÚRGICO: Mandamos el valor real de la DB al Front
                "cantidad": gasto.cantidad if gasto.cantidad else 1
            }
            lista_final.append(gasto_dict)
            
        return lista_final