from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from models.arqueo import ArqueoTurno
from models.gastos import Gasto
from models.tsventas import tsventas
from models.acpm import AcpmLog
from models.ocupacion import Ocupacion 
from models.proveedor import Proveedor 
from models.room import tshabitacion

class ArqueoService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_turno_activo(self, usuario_id: int):
        return (
            self.db.query(ArqueoTurno)
            .filter(
                ArqueoTurno.id_usuario == usuario_id,
                ArqueoTurno.fecha_fin == None
            )
            .order_by(ArqueoTurno.id_arqueo.desc())
            .first()
        )

    def obtener_detalle_arqueos(self, id_arqueo: int):
        arqueo = self.db.query(ArqueoTurno).filter(ArqueoTurno.id_arqueo == id_arqueo).first()
        if not arqueo:
            return None

        # 1. GASTOS
        query_gastos = self.db.query(
            Gasto,
            Proveedor.nombre.label("nombre_proveedor")
        ).join(
            Proveedor, Gasto.id_proveedor == Proveedor.id_proveedor, isouter=True
        ).filter(Gasto.id_arqueo == id_arqueo).all()

        lista_gastos_formateada = []
        g_contado = 0.0
        g_credito = 0.0 # Agregamos para el desglose
        for g, nom_prov in query_gastos:
            valor = float(g.valor or 0)
            tipo = str(g.tipo_pago).lower() if g.tipo_pago else ""
            
            if 'contado' in tipo: 
                g_contado += valor
            else:
                g_credito += valor
                
            lista_gastos_formateada.append({
                "concepto": g.concepto, 
                "valor": valor,
                "nombre_proveedor": nom_prov or g.proveedor or "General",
                "tipo_pago": g.tipo_pago
            })

        # 2. HABITACIONES (Calculando medios de pago)
        query_habs = self.db.query(
            Ocupacion, 
            tshabitacion.numhabitacion 
        ).join(
            tshabitacion, Ocupacion.id_habitacion == tshabitacion.id_habitacion
        ).filter(Ocupacion.id_arqueo == id_arqueo).all()

        v_nequi = 0.0
        v_datafono = 0.0
        habitaciones_list = []
        
        for h_obj, h_num in query_habs:
            valor_hab = float(h_obj.total_pagar or 0)
            metodo = str(h_obj.metodo_pago).upper() if h_obj.metodo_pago else "EFECTIVO"
            
            if "NEQUI" in metodo: v_nequi += valor_hab
            if "DATAFONO" in metodo: v_datafono += valor_hab
            
            habitaciones_list.append({
                "numhabitacion": f"{h_num}", 
                "total": valor_hab, 
                "hora": h_obj.hora_salida.strftime("%H:%M") if h_obj.hora_salida else "--:--"
            })

        # 3. ACPM (Separando contado y crédito)
        lista_acpm = self.db.query(AcpmLog).filter(AcpmLog.id_arqueo == id_arqueo).all()
        acpm_contado = 0.0
        acpm_credito = 0.0
        acpm_list = []
        for a in lista_acpm:
            v_acpm = float(a.valor_total or 0)
            if str(a.tipo_pago).lower() == 'contado': acpm_contado += v_acpm
            else: acpm_credito += v_acpm
            acpm_list.append({
                "proveedor": a.proveedor or "Suministro",
                "valor": v_acpm,
                "total": v_acpm,
                

            })

        # 4. CONSUMOS
        lista_consumos = self.db.query(tsventas).filter(tsventas.id_arqueo == id_arqueo).all()
        consumos_list = [
            {
                "concepto": c.concepto or "Producto",
                "total": float(c.total or c.tsvalor or 0)
            } for c in lista_consumos
        ]

        v_habs = sum(h['total'] for h in habitaciones_list)
        v_consumos = sum(c['total'] for c in consumos_list)
        
        # ... (código de cálculos anterior igual) ...

        # ... (Mantén todos tus cálculos anteriores igual)

        return {
            "id_arqueo": arqueo.id_arqueo,
            "consecutivo": arqueo.consecutivo,
            "fecha_inicio": arqueo.fecha_inicio,
            "fecha_fin": arqueo.fecha_fin,
            "neto": float(arqueo.neto or 0),
            
            # Encabezado
            "total_ventas": v_habs + v_consumos,
            "total_habitaciones": v_habs,
            "total_dinero_hab": v_habs, 
            "ventas_nequi": v_nequi,
            "ventas_datafono": v_datafono,
            "acpm_contado": acpm_contado,
            "acpm_credito": acpm_credito,
            "gastos_contado": g_contado,
            "gastos_credito": g_credito,

            # Listas Detalladas (Asegura que el Front las vea)
            "habitaciones": habitaciones_list,
            "ventas": habitaciones_list,  # Redundancia para el detalle de habs
            "gastos": lista_gastos_formateada,
            "detalles_gastos": lista_gastos_formateada, # Nombre alternativo frecuente
            "acpm_detalles": acpm_list,
            "acpm": acpm_list, # Nombre alternativo frecuente
            "detalles": consumos_list
        }
    
    # ... (cerrar_turno se mantiene igual)

    def cerrar_turno(self, usuario_id: int):
        turno = self.obtener_turno_activo(usuario_id)
        if not turno:
            return {"ok": False, "message": "No hay turno activo"}

        # ✅ Marca ocupaciones cerradas con el ID de este arqueo
        self.db.query(Ocupacion).filter(
            Ocupacion.id_arqueo == None, 
            Ocupacion.estado == "LIBERADA"
        ).update({"id_arqueo": turno.id_arqueo}, synchronize_session=False)

        # ✅ Marca Gastos y ACPM
        self.db.query(Gasto).filter(Gasto.id_arqueo == None).update({"id_arqueo": turno.id_arqueo})
        self.db.query(AcpmLog).filter(AcpmLog.id_arqueo == None).update({"id_arqueo": turno.id_arqueo})

        # ✅ Cierra el turno
        turno.fecha_fin = func.now()
        turno.estado = "CERRADO"

        # ✅ También marcamos los consumos de patio/habitacion con este arqueo
        #self.db.query(tsventas).filter(tsventas.id_arqueo == None).update({"id_arqueo": turno.id_arqueo})
        # ✅ Esto "atrapa" todo lo que estaba suelto y lo asigna al turno que se está cerrando
# Así, el próximo turno empezará de cero (limpio)
        self.db.query(tsventas).filter(tsventas.id_arqueo == None).update({"id_arqueo": turno.id_arqueo})
        self.db.query(Gasto).filter(Gasto.id_arqueo == None).update({"id_arqueo": turno.id_arqueo})
        self.db.query(AcpmLog).filter(AcpmLog.id_arqueo == None).update({"id_arqueo": turno.id_arqueo})


        
        self.db.commit()
        return {"ok": True, "id_arqueo": turno.id_arqueo}