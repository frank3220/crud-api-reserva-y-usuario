from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from models.ocupacion import Ocupacion, EstadoOcupacion
from models.room import tshabitacion
from schemas.ocupacion import OcupacionCreate, OcupacionUpdate
from models.arqueo_actual import ArqueoActual
from models.arqueo import ArqueoTurno  # ✅ IMPORTANTE: Añadimos el modelo de Arqueo
from services.config_service import ConfigService

from models.usuario import Usuario           

class OcupacionService:
    def __init__(self, db: Session):
        self.db = db
        self.config = ConfigService(db)

    # ------------------------------------------------------
    # SUMAR AL ARQUEO ACTUAL (Se mantiene igual)
    # ------------------------------------------------------
    def _sumar_a_arqueo_actual(self, monto: float, metodo: str = "efectivo"):
        if monto is None: return
        arqueo = self.db.query(ArqueoActual).filter(ArqueoActual.id == 1).first()
        if not arqueo:
            arqueo = ArqueoActual(id=1, total_ventas=0, total_acpm=0, total_gastos=0)
            self.db.add(arqueo)
            self.db.commit()
            self.db.refresh(arqueo)

        arqueo.total_ventas += float(monto)
        metodo_limpio = metodo.lower() if metodo else "efectivo"
        
        if metodo_limpio == "nequi" and hasattr(arqueo, 'ventas_nequi'):
            arqueo.ventas_nequi += float(monto)
        elif metodo_limpio == "datafono" and hasattr(arqueo, 'ventas_datafono'):
            arqueo.ventas_datafono += float(monto)
        elif hasattr(arqueo, 'ventas_efectivo'):
            arqueo.ventas_efectivo += float(monto)
        self.db.commit()

    # ------------------------------------------------------
    # CHECK-IN (ACTUALIZADO PARA AMANECIDAS)
    # ------------------------------------------------------
    # ------------------------------------------------------
    # CHECK-IN (¡SUPER-BLINDADO CONTRA TARIFAS EN $0!)
    # ------------------------------------------------------
    def crear_ocupacion(self, data: OcupacionCreate, id_cajero: int):
        # 🌟 PASO 0: Aseguramos el dinero del front en el primer milisegundo
        tarifa_inyectada = getattr(data, 'tarifa', None) or getattr(data, 'total_pagar', None) or getattr(data, 'precio_2h', None)
        precio_final = float(tarifa_inyectada) if (tarifa_inyectada and float(tarifa_inyectada) > 0) else 0.0

        # 1. Verificar si existe la habitación
        room = self.db.query(tshabitacion).filter(tshabitacion.id_habitacion == data.id_habitacion).first()
        if not room:
            raise HTTPException(404, "La habitación no existe.")

        # 2. Cerrar cualquier ocupación activa previa en esa habitación (por seguridad)
        ocupacion_activa = self.db.query(Ocupacion).filter(
            Ocupacion.id_habitacion == data.id_habitacion,
            Ocupacion.hora_salida.is_(None),
        ).first()

        if ocupacion_activa:
            ocupacion_activa.hora_salida = datetime.now()
            ocupacion_activa.estado = EstadoOcupacion.LIBERADA
            ocupacion_activa.activa = False
            # 💡 Quitamos el commit intermedio para que no interfiera con los datos en memoria

        # 3. Lógica Maestra de Precios Dinámicos
        if data.es_amanecida:
            # Si es amanecida y el precio se rescató en 0, le ponemos el precio base como último recurso
            if precio_final == 0.0 and room and room.precio_2h:
                precio_final = float(room.precio_2h)
        else:
            # Si es por horas normales, no amarramos precio fijo al entrar (se calcula al salir)
            precio_final = None

        # 4. Crear el registro de ocupación
        nueva = Ocupacion(
            id_habitacion=data.id_habitacion,
            hora_entrada=datetime.now(),
            estado=EstadoOcupacion.OCUPADA,
            activa=True,
            observaciones=data.observaciones,
            total_pagar=precio_final,  # 🌟 ¡Aquí viaja el dinero real asegurado!
            usuario_id=id_cajero,
        )

        # 5. Cambiar color/estado de la habitación para el Dashboard
        if data.es_amanecida:
            room.estado = "A"  # 'A' activa la tarjeta naranja/fucsia de amanecida
        else:
            room.estado = "OCUPADA" # Color rojo normal
        room.activa = True    
        room.hora_limpiar = None

        # 6. Guardar todo junto en una sola transacción limpia
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        
        return nueva

    # ------------------------------------------------------
    # CHECK-OUT (CON EL ARREGLO BLINDADO)
    # ------------------------------------------------------
    # ------------------------------------------------------
    # CHECK-OUT (CON EL ARREGLO BLINDADO PARA AMANECIDAS)
    # ------------------------------------------------------
    # ------------------------------------------------------
    # CHECK-OUT (CON EL ARREGLO BLINDADO PARA AMANECIDAS - PLAN B)
    # ------------------------------------------------------
    def cerrar_ocupacion(self, ocupacion_id: int, data: OcupacionUpdate):
        ocup = self.db.query(Ocupacion).filter(Ocupacion.id_ocupacion == ocupacion_id).first()
        if not ocup:
            raise HTTPException(404, "La ocupación no existe.")

        if ocup.hora_salida:
            raise HTTPException(400, "La ocupación ya estaba cerrada.")

        turno_activo = self.db.query(ArqueoTurno).filter(
            ArqueoTurno.id_usuario == data.usuario_id,
            ArqueoTurno.fecha_fin == None
        ).order_by(ArqueoTurno.id_arqueo.desc()).first()

        # --- 🛡️ ARREGLO MAESTRO BLINDADO CONTRA CORTESÍAS ---
        monto_final = data.total_pagar
        metodo_pago_limpio = (data.metodo_pago or "").lower()

        if metodo_pago_limpio == "gracia_sin_cobro":
            monto_final = 0
        else:
            if ocup.total_pagar and ocup.total_pagar > 0:
                if not monto_final or monto_final == 0:
                    monto_final = ocup.total_pagar
        # ---------------------------------------------------

        ocup.hora_salida = datetime.now()
        ocup.estado = EstadoOcupacion.LIBERADA     
        ocup.activa = False
        ocup.total_pagar = monto_final 
        ocup.metodo_pago = data.metodo_pago 

        # 🚀 REGLA DE ORO PLAN B: Buscamos si la habitación estaba en fucsia ("A") o si el front mandó True
        room = self.db.query(tshabitacion).filter(tshabitacion.id_habitacion == ocup.id_habitacion).first()
        
        es_amanecida_solicitada = getattr(data, 'es_amanecida', False) or (room and room.estado == "A")

        if es_amanecida_solicitada:
            # 1. Intentamos guardar en el campo booleano normal
            if hasattr(ocup, 'es_amanecida'):
                ocup.es_amanecida = True
            
            # 2. 🔥 EL SEGURO: Forzamos la palabra en las observaciones. 
            # Como tu consulta de ventas busca la palabra "amanecida" en el texto, esto lo va a activar sí o sí.
            if ocup.observaciones:
                if "amanecida" not in ocup.observaciones.lower():
                    ocup.observaciones = f"{ocup.observaciones} - AMANECIDA"
            else:
                ocup.observaciones = "AMANECIDA"

        if turno_activo:
            ocup.id_arqueo = turno_activo.id_arqueo

        if hasattr(ocup, 'id_usuario_salida'):
            ocup.id_usuario_salida = data.usuario_id 
    
        self._sumar_a_arqueo_actual(float(monto_final), data.metodo_pago)

        if room:
            minutos = self.config.get("minutos_limpieza", 5)
            room.estado = "LIMPIEZA"
            room.hora_limpiar = datetime.now() + timedelta(minutes=minutos)

        self.db.commit()
        self.db.refresh(ocup)
        return ocup
    # ------------------------------------------------------
    # ANULAR/ELIMINAR (AUDITORÍA: QUIÉN ELIMINA)
    # ------------------------------------------------------
    def anular_ocupacion(self, ocupacion_id: int, id_cajero: int):
        ocup = self.db.query(Ocupacion).filter(Ocupacion.id_ocupacion == ocupacion_id).first()
        if not ocup:
            raise HTTPException(404, "Ocupación no encontrada.")

        ocup.estado = "ANULADA"
        ocup.activa = False
        
        # Auditoría de eliminación
        if hasattr(ocup, 'id_usuario_anulacion'):
            ocup.id_usuario_anulacion = id_cajero
            ocup.fecha_anulacion = datetime.now()

        room = self.db.query(tshabitacion).filter(tshabitacion.id_habitacion == ocup.id_habitacion).first()
        if room:
            room.estado = "DISPONIBLE"
            room.hora_limpiar = None

        self.db.commit()
        return {"status": "ok", "message": "Habitación anulada correctamente"}

    # ------------------------------------------------------
    # OBTENER DATOS PARA TICKET (CON TODOS LOS DETALLES)
    # ------------------------------------------------------
    def obtener_ocupacion_para_ticket(self, ocupacion_id: int):
        from models.consumo import Consumo
        from models.usuario import Usuario

        ocup = self.db.query(Ocupacion).filter(Ocupacion.id_ocupacion == ocupacion_id).first()
        if not ocup:
            raise HTTPException(404, "Ocupación no encontrada.")

        room = self.db.query(tshabitacion).filter(tshabitacion.id_habitacion == ocup.id_habitacion).first()

        usuario_nombre = ""
        if ocup.usuario_id:
            usuario = self.db.query(Usuario).filter(Usuario.idusuario == ocup.usuario_id).first()
            if usuario:
                usuario_nombre = usuario.nombre

        consumos = self.db.query(Consumo).filter(Consumo.id_ocupacion == ocupacion_id).all()
        lista_consumos = [
            {
                "concepto": c.concepto,
                "cantidad": c.cantidad,
                "valor": float(c.valor),
                "total": float(c.valor * c.cantidad),
            }
            for c in consumos
        ]

        total_consumos = sum(c["total"] for c in lista_consumos)
        total_pagar = float(ocup.total_pagar or 0)

        # Cálculo de tiempo de estadía
        tiempo = ""
        if ocup.hora_entrada and ocup.hora_salida:
            diff = ocup.hora_salida - ocup.hora_entrada
            minutos = int(diff.total_seconds() // 60)
            horas = minutos // 60
            mins = minutes = minutos % 60
            tiempo = f"{horas}h {mins}m"

        return {
            "motel": "Motel Donde Mama",
            "habitacion": room.numhabitacion if room else "",
            "tipo": room.tipo if room else "",
            "entrada": ocup.hora_entrada,
            "salida": ocup.hora_salida,
            "tiempo": tiempo,
            "usuario": usuario_nombre,
            "total_habitacion": float(total_pagar - total_consumos),
            "consumos": lista_consumos,
            "total_consumos": total_consumos,
            "total": total_pagar,
            "fecha": ocup.hora_salida,
            "metodo_pago": ocup.metodo_pago if hasattr(ocup, 'metodo_pago') else "efectivo",
            # 🔥 CORRECCIÓN AQUÍ: Mandamos si es amanecida al frontend
            "es_amanecida": getattr(ocup, 'es_amanecida', False) or "amanecida" in (ocup.observaciones or "").lower()
        }

    # ------------------------------------------------------
    # REPORTE DE AUDITORÍA DETALLADO
    # ------------------------------------------------------
    def obtener_reporte_auditoria(self):
        from sqlalchemy.orm import aliased
        from models.usuario import Usuario

        u_ent = aliased(Usuario)
        u_sal = aliased(Usuario)
        u_anu = aliased(Usuario)

        query = self.db.query(
            Ocupacion,
            u_ent.nombre.label("nombre_entrada"),
            u_sal.nombre.label("nombre_salida"),
            u_anu.nombre.label("nombre_anulacion"),
            tshabitacion.numhabitacion
        ).join(tshabitacion, Ocupacion.id_habitacion == tshabitacion.id_habitacion)\
         .outerjoin(u_ent, Ocupacion.usuario_id == u_ent.idusuario)\
         .outerjoin(u_sal, Ocupacion.id_usuario_salida == u_sal.idusuario)\
         .outerjoin(u_anu, Ocupacion.id_usuario_anulacion == u_anu.idusuario)\
         .order_by(Ocupacion.hora_entrada.desc()).all()

        reporte = []
        for ocup, n_ent, n_sal, n_anu, num_hab in query:
            reporte.append({
                "id_ocupacion": ocup.id_ocupacion,
                "habitacion": num_hab,
                "entrada": ocup.hora_entrada,
                "salida": ocup.hora_salida,
                "anulacion": ocup.fecha_anulacion,
                "estado": ocup.estado,
                "usuario_entrada": n_ent or "Sistema",
                "usuario_salida": n_sal or ("-" if ocup.estado != "LIBERADA" else "N/A"),
                "usuario_anulacion": n_anu or ("-" if ocup.estado != "ANULADA" else "N/A"),
                "total": float(ocup.total_pagar or 0),
                "metodo_pago": ocup.metodo_pago or "Efectivo"
        })
        return reporte
    



    # ------------------------------------------------------
    # VENTA DE HABITACIONES DEL TURNO ACTUAL (Dashboard Derecho)
    # ------------------------------------------------------
    def obtener_ventas_turno_actual(self, id_usuario: int):
        # 1. Identificar el turno/arqueo que tiene abierto el cajero actual
        turno_activo = self.db.query(ArqueoTurno).filter(
            ArqueoTurno.id_usuario == id_usuario,
            ArqueoTurno.fecha_fin == None
        ).order_by(ArqueoTurno.id_arqueo.desc()).first()

        if not turno_activo:
            return {
                "ventas": [],
                "total_amanecidas_cantidad": 0
            }

        # 2. Consultar solo las ocupaciones de este arqueo que NO estén anuladas
        query = self.db.query(Ocupacion, tshabitacion.numhabitacion).join(
            tshabitacion, Ocupacion.id_habitacion == tshabitacion.id_habitacion
        ).filter(
            Ocupacion.id_arqueo == turno_activo.id_arqueo,
            Ocupacion.estado == EstadoOcupacion.LIBERADA  # 🚨 FILTRO MAESTRO: Solo las facturadas/cerradas con éxito
        ).order_by(Ocupacion.hora_salida.desc()).all()

        ventas = []
        contador_amanecidas = 0
        
        for ocup, num_hab in query:
            total_cobrado = float(ocup.total_pagar or 0)
            
            # 🚨 REGLA QUIRÚRGICA 1: Si se liberó sin cobrar ($0), NO ensucia la lista principal de la tirilla
            if total_cobrado == 0:
                continue

            # 🔥 DETECTOR DE AMANECIDA: Evaluamos si el registro se marcó como amanecida
            es_amanecida_real = (
                getattr(ocup, 'es_amanecida', False) == True or 
                getattr(ocup, 'es_amanecida', 0) == 1 or
                "amanecida" in (ocup.observaciones or "").lower()
            )
            
            if es_amanecida_real:
                contador_amanecidas += 1

            ventas.append({
                "id_ocupacion": ocup.id_ocupacion,
                "habitacion": num_hab,
                "salida": ocup.hora_salida,
                "total": total_cobrado,
                "metodo_pago": ocup.metodo_pago or "Efectivo",
                "es_amanecida": es_amanecida_real
            })
            
        # 🚀 REGLA QUIRÚRGICA 2: Retornamos la estructura limpia junto con el contador exacto para mamá
        return {
            "ventas": ventas,
            "total_amanecidas_cantidad": contador_amanecidas
        }