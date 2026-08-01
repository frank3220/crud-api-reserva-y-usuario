from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependencies.database import get_db

from datetime import datetime, date, time, timedelta, timezone

from models.ocupacion import Ocupacion
from models.room import tshabitacion
from models.acpm import AcpmLog
from models.arqueo import ArqueoTurno
from models.gastos import Gasto
from models.consumo import Consumo
from models.compras_proveedor import ComprasProveedor
from models.compra_detalle import CompraDetalle
from models.producto import Producto
from models.proveedor import Proveedor



# Zona horaria Colombia
COLOMBIA_TZ = timezone(timedelta(hours=-5))

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------
def ahora_co() -> datetime:
    """Datetime NAIVE en hora Colombia (sin tzinfo) para BD."""
    return datetime.now(COLOMBIA_TZ).replace(tzinfo=None)

def rango_dia(fecha: date):
    inicio = datetime.combine(fecha, time.min)
    fin = datetime.combine(fecha, time.max)
    return inicio, fin

def obtener_turno_activo(db: Session):
    return (
        db.query(ArqueoTurno)
        .filter(ArqueoTurno.fecha_fin == None)
        .order_by(ArqueoTurno.id_arqueo.desc())
        .first()
    )

def asegurar_turno_activo(db: Session):
    """Si no hay turno activo, crea uno nuevo."""
    turno = obtener_turno_activo(db)
    if turno:
        return turno

    ultimo = db.query(ArqueoTurno).order_by(ArqueoTurno.consecutivo.desc()).first()
    consecutivo = (ultimo.consecutivo + 1) if ultimo else 1

    nuevo = ArqueoTurno(
        consecutivo=consecutivo,
        fecha_inicio=ahora_co(),
        fecha_fin=None,
        total_ventas=0,
        total_acpm=0,
        total_gastos=0,
        total_consumos=0,
        neto=0,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ----------------------------------------------------------
# RESUMEN GENERAL
# ----------------------------------------------------------
@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):

    hoy = datetime.now(COLOMBIA_TZ).date()
    inicio_dia, fin_dia = rango_dia(hoy)

    total_habs = db.query(tshabitacion).count()
    ocupadas = db.query(Ocupacion).filter(Ocupacion.hora_salida == None).count()
    disponibles = total_habs - ocupadas

    # ✅ "Ventas hoy" debe ser SOLO del TURNO ACTIVO (pendientes)
    turno = asegurar_turno_activo(db)
    inicio_turno = turno.fecha_inicio
    fin_turno = ahora_co()

    ventas_turno = (
        db.query(Ocupacion)
        .filter(
            Ocupacion.hora_salida != None,
            Ocupacion.total_pagar != None,
            Ocupacion.hora_salida >= inicio_turno,
            Ocupacion.hora_salida <= fin_turno,
            Ocupacion.id_arqueo == None,
        )
        .all()
    )
    total_hoy = sum(float(o.total_pagar or 0) for o in ventas_turno)

    # total del mes real
    inicio_mes = date(hoy.year, hoy.month, 1)
    inicio_m, _ = rango_dia(inicio_mes)

    ventas_mes = (
        db.query(Ocupacion)
        .filter(
            Ocupacion.hora_salida >= inicio_m,
            Ocupacion.hora_salida <= fin_dia,
            Ocupacion.total_pagar != None,
        )
        .all()
    )
    total_mes = sum(float(o.total_pagar or 0) for o in ventas_mes)

    # -------------------------
# COMPRAS PROVEEDOR CONTADO (PARA DASHBOARD)
# -------------------------
    compras_rows = (
        db.query(ComprasProveedor)
        .filter(
            ComprasProveedor.id_arqueo == None,
            ComprasProveedor.tipo_pago == "contado",
            func.date(ComprasProveedor.fecha) == hoy,
    )
    .all()
)

    total_compras = sum(float(c.total or 0) for c in compras_rows)


    return {
        "occupied": ocupadas,
        "available": disponibles,
        "total_today": total_hoy,
        "month_total": total_mes,
        "total_compras": total_compras,  # 👈 NUEVO
    }

# ----------------------------------------------------------
# ✅ LISTA DE VENTAS SOLO DEL TURNO ACTIVO (PENDIENTES)
# GET /dashboard/ventas-turno
# ----------------------------------------------------------
@router.get("/ventas-turno")
def ventas_turno_activo(db: Session = Depends(get_db)):
    turno = asegurar_turno_activo(db)
    inicio = turno.fecha_inicio
    fin = ahora_co()

    habitaciones = {h.id_habitacion: h for h in db.query(tshabitacion).all()}

    ocupaciones = (
        db.query(Ocupacion)
        .filter(
            Ocupacion.hora_salida != None,
            Ocupacion.total_pagar != None,
            Ocupacion.hora_salida >= inicio,
            Ocupacion.hora_salida <= fin,
            Ocupacion.id_arqueo == None,
        )
        .order_by(Ocupacion.hora_salida.desc())
        .all()
    )

    lista = []
    for o in ocupaciones:
        hab = habitaciones.get(o.id_habitacion)
        lista.append({
            "id_ocupacion": o.id_ocupacion,
            "id_habitacion": o.id_habitacion,
            "numhabitacion": hab.numhabitacion if hab else "",
            "hora_entrada": o.hora_entrada,
            "hora_salida": o.hora_salida,
            "total": float(o.total_pagar or 0),
            
        })

    return {"ok": True, "ventas": lista}

# ----------------------------------------------------------
# LISTAR ARQUEOS
# ----------------------------------------------------------
@router.get("/arqueos")
def listar_arqueos(db: Session = Depends(get_db)):

    arqueos = db.query(ArqueoTurno).order_by(ArqueoTurno.consecutivo.desc()).all()

    resp = []
    for a in arqueos:
        resp.append({
            "id_arqueo": a.id_arqueo,
            "consecutivo": a.consecutivo,
            "fecha_inicio": a.fecha_inicio,
            "fecha_fin": a.fecha_fin,
            "total_ventas": float(a.total_ventas or 0),
            "total_acpm": float(a.total_acpm or 0),
            "total_gastos": float(a.total_gastos or 0),
            "total_consumos": float(a.total_consumos or 0),
            "neto": float(a.neto or 0),
            "creado_en": getattr(a, "creado_en", None),
        })

    return resp

# ----------------------------------------------------------
# ----------------------------------------------------------
# --- REEMPLAZA ESTA FUNCIÓN EN TU BACKEND ---
# ----------------------------------------------------------
# --- REEMPLAZA ESTA FUNCIÓN EN TU BACKEND ---
# ----------------------------------------------------------
@router.get("/arqueos/{id_arqueo}")
def detalle_arqueo(id_arqueo: int, db: Session = Depends(get_db)):
    # 1. Buscar el arqueo histórico
    arqueo = db.query(ArqueoTurno).filter(ArqueoTurno.id_arqueo == id_arqueo).first()
    if not arqueo:
        return {"error": "No existe el arqueo"}

    # --- 1. VENTAS HABITACIONES ---
    ventas_rows = db.query(Ocupacion).filter(Ocupacion.id_arqueo == id_arqueo).all()
    habitaciones_map = {h.id_habitacion: h for h in db.query(tshabitacion).all()}
    
    total_ventas_habitaciones = 0.0
    v_nequi = 0.0
    v_datafono = 0.0
    conteo_habitaciones = 0
    cantidad_amanecidas = 0  # 🚀 NUEVO: Contador de amanecidas cobradas para la reimpresión
    ventas_list = []

    for o in ventas_rows:
        valor_pagar = float(o.total_pagar or 0)
        
        # 🚨 FILTRO MAESTRO: Si la habitación se liberó sin cobrar ($0), NO entra en la tirilla
        if valor_pagar == 0:
            continue

        total_ventas_habitaciones += valor_pagar
        conteo_habitaciones += 1
        
        metodo = str(o.metodo_pago or "efectivo").lower().replace("é", "e").strip()
        if "nequi" in metodo: 
            v_nequi += valor_pagar
        elif "datafono" in metodo or "tarjeta" in metodo: 
            v_datafono += valor_pagar

        hab = habitaciones_map.get(o.id_habitacion)
        
        # 🧠 DETECTOR AUTOMÁTICO POR TEXTO DE REGISTRO (Fiel al Plan B exitoso)
        obs = str(o.observaciones or "").lower()
        es_amanecida_real = (o.estado == "A") or ("amanec" in obs)

        if es_amanecida_real:
            cantidad_amanecidas += 1  # 🚀 Si se detecta la marca, la sumamos al total

        ventas_list.append({
            "hab": f"Hab {hab.numhabitacion}" if hab else "N/A",
            "numhabitacion": hab.numhabitacion if hab else "N/A",
            "horario": f"{o.hora_entrada.strftime('%H:%M')} - {o.hora_salida.strftime('%H:%M')}" if o.hora_entrada and o.hora_salida else "N/A",
            "hora_entrada": o.hora_entrada.strftime("%H:%M") if o.hora_entrada else "N/A",
            "hora_salida": o.hora_salida.strftime("%H:%M") if o.hora_salida else "N/A",
            "total": valor_pagar,
            "es_amanecida_real": es_amanecida_real
        })

    # --- 2. CONSUMOS DE PATIO ---
    consumo_rows = db.query(Consumo).filter(Consumo.id_arqueo == id_arqueo).all()
    total_consumos_patio = sum(float(c.valor or 0) * (c.cantidad or 1) for c in consumo_rows if not getattr(c, "id_ocupacion", None))
    
    consumos_agrupados = {}
    for c in consumo_rows:
        nombre = (getattr(c, "nombre_producto", None) or getattr(c, "concepto", "VARIOS")).upper()
        cant = int(c.cantidad or 1)
        subtotal = float(c.valor or 0) * cant
        if nombre in consumos_agrupados:
            consumos_agrupados[nombre]["cant"] += cant
            consumos_agrupados[nombre]["total"] += subtotal
        else:
            consumos_agrupados[nombre] = {"nombre": nombre, "cant": cant, "total": subtotal}

    # --- 3. COMPRAS PROVEEDOR ---
    compras_rows = db.query(ComprasProveedor).filter(ComprasProveedor.id_arqueo == id_arqueo).all()
    total_compras_contado = sum(float(cp.total or 0) for cp in compras_rows if "credito" not in str(cp.tipo_pago or "").lower())
    total_compras_credito = sum(float(cp.total or 0) for cp in compras_rows if "credito" in str(cp.tipo_pago or "").lower())

    # --- 4. GASTOS ---
    gastos_puros_rows = db.query(Gasto).filter(Gasto.id_arqueo == id_arqueo, Gasto.concepto.ilike("%compra proveedor%") == False).all()
    total_gastos_contado = sum(float(g.valor or 0) for g in gastos_puros_rows if "credito" not in str(g.tipo_pago or "").lower())
    total_gastos_credito = sum(float(g.valor or 0) for g in gastos_puros_rows if "credito" in str(g.tipo_pago or "").lower())

    # --- 5. ACPM ---
    acpm_rows = db.query(AcpmLog).filter(AcpmLog.id_arqueo == id_arqueo).all()
    total_acpm_contado = sum(float(a.valor_total or 0) for a in acpm_rows if "credito" not in str(a.tipo_pago or "").lower())
    total_acpm_credito = sum(float(a.valor_total or 0) for a in acpm_rows if "credito" in str(a.tipo_pago or "").lower())

    # --- DETALLES ACPM ---
    detalles_acpm_list = []
    total_litros_acpm = 0
    for a in acpm_rows:
        cant = int(getattr(a, "cantidad_litros", 0) or getattr(a, "cantidad", 0) or getattr(a, "litros", 0))
        total_litros_acpm += cant
        tipo_label = "CRED" if "credito" in str(a.tipo_pago or "").lower() else "CONT"
        prov = getattr(a, "proveedor", "S.N")
        nombre_prov = prov.nombre if hasattr(prov, 'nombre') else str(prov)
        detalles_acpm_list.append({
            "proveedor": nombre_prov.upper(),
            "litros": cant,
            "tipo": tipo_label,
            "total": float(a.valor_total or 0)
        })

    # --- DETALLES DE GASTOS ---
    detalles_gastos_list = []
    for g in gastos_puros_rows:
        detalles_gastos_list.append({
            "descripcion": str(g.concepto or "GASTO").upper(),
            "tipo": "CRED" if "credito" in str(g.tipo_pago or "").lower() else "CONT",
            "total": float(g.valor or 0)
        })

    # --- DETALLES DE COMPRAS ---
    detalles_compras_list = []
    for cp in compras_rows:
        nombre_prov = "S.N"
        if cp.proveedor and hasattr(cp.proveedor, 'nombre'):
            nombre_prov = cp.proveedor.nombre
        
        if not cp.detalles:
            detalles_compras_list.append({
                "producto": "COMPRA GENERAL",
                "proveedor": nombre_prov.upper(),
                "cantidad": 1,
                "tipo": "CRED" if "credito" in str(cp.tipo_pago or "").lower() else "CONT",
                "total": float(cp.total or 0)
            })
        else:
            for det in cp.detalles:
                nombre_articulo = "PRODUCTO"
                if hasattr(det, 'producto_rel') and det.producto_rel:
                    nombre_articulo = getattr(det.producto_rel, 'nombre', "PRODUCTO")
                elif hasattr(det, 'nombre_producto'):
                    nombre_articulo = det.nombre_producto
                else:
                    nombre_articulo = f"ART. ID:{det.id_producto}"

                valor_detalle = float(det.cantidad or 0) * float(det.costo_unitario or 0)

                detalles_compras_list.append({
                    "producto": str(nombre_articulo).upper(),
                    "proveedor": nombre_prov.upper(),
                    "cantidad": int(det.cantidad or 1),
                    "tipo": "CRED" if "credito" in str(cp.tipo_pago or "").lower() else "CONT",
                    "total": valor_detalle
                })

    total_ventas_final = total_ventas_habitaciones + total_consumos_patio 
    neto = total_ventas_final - v_nequi - v_datafono - total_acpm_contado - total_gastos_contado - total_compras_contado

    return {
        "ok": True,
        "resumen": {
            "total_ventas": total_ventas_final,
            "neto": neto,
            "ventas_nequi": v_nequi,
            "ventas_datafono": v_datafono,
            "total_acpm_contado": total_acpm_contado,
            "total_gastos_contado": total_gastos_contado,
            "total_compras_contado": total_compras_contado,
            "total_acpm_credito": total_acpm_credito,
            "total_gastos_credito": total_gastos_credito,
            "total_compras_credito": total_compras_credito,
            "cant_habitaciones": conteo_habitaciones,
            "total_dinero_hab": total_ventas_habitaciones,
            "total_litros_acpm": total_litros_acpm,
            "total_amanecidas_cantidad": cantidad_amanecidas  # 🚀 ENVIADO AL FRONTEND: El total de amanecidas contadas
        },
        "detalles_habitaciones": ventas_list,
        "habitaciones": ventas_list, 
        "ventas": ventas_list,      
        "detalles_consumos": list(consumos_agrupados.values()),
        "detalles_acpm": detalles_acpm_list,
        "detalles_gastos": detalles_gastos_list,
        "detalles_compras": detalles_compras_list
    }
# ----------------------------------------------------------
# ✅ RESUMEN DEL TURNO ACTIVO
# GET /dashboard/arqueo-turno
# ----------------------------------------------------------
# ----------------------------------------------------------
# ✅ RESUMEN DEL TURNO ACTIVO (DETALLE DE VENTAS Y CONSUMOS)
# ----------------------------------------------------------
# ----------------------------------------------------------
# ✅ RESUMEN DEL TURNO ACTIVO (DETALLE DE VENTAS Y CONSUMOS)
# ----------------------------------------------------------
@router.get("/arqueo-turno")
def arqueo_turno_activo(db: Session = Depends(get_db)):
    # 1. Obtenemos el turno que está abierto actualmente
    turno = asegurar_turno_activo(db)
    id_actual = turno.id_arqueo
    fin = ahora_co()

    # --- 1. VENTAS HABITACIONES ---
    from sqlalchemy import or_

    ventas_rows = db.query(Ocupacion).filter(
        Ocupacion.id_arqueo == None,  # Que no hayan sido arqueadas antes
        or_(
            (Ocupacion.hora_salida != None), 
            (Ocupacion.estado == "A")
        ),
    ).order_by(Ocupacion.hora_salida.desc()).all()

    habitaciones = {h.id_habitacion: h for h in db.query(tshabitacion).all()}
    
    ventas_list = []
    total_ventas_habitaciones = 0.0
    v_nequi = 0.0
    v_datafono = 0.0
    conteo_habitaciones = 0 

    for o in ventas_rows:
        hab = habitaciones.get(o.id_habitacion)
        valor_pagar = float(o.total_pagar or 0)
        total_ventas_habitaciones += valor_pagar
        conteo_habitaciones += 1 

        metodo = str(o.metodo_pago or "efectivo").lower().replace("é", "e").strip()
        if "nequi" in metodo:
            v_nequi += valor_pagar
        elif "datafono" in metodo or "tarjeta" in metodo:
            v_datafono += valor_pagar

        # 🧠 DETECTOR INTELIGENTE RE-EVOLUCIONADO (Fiel al botón y protegido al cerrar)
        # 🧠 DETECTOR AUTOMÁTICO POR TEXTO DE REGISTRO (Sin precios amarrados)
        obs = str(o.observaciones or "").lower()
        
        # El sistema solo busca si en la observación dice "amanecida" o si el estado está en "A"
        es_amanecida_real = (o.estado == "A") or ("amanec" in obs)

        ventas_list.append({
            "id_ocupacion": o.id_ocupacion,
            "id_habitacion": o.id_habitacion,
            "numhabitacion": hab.numhabitacion if hab else "N/A",
            "hora_entrada": o.hora_entrada.strftime("%H:%M") if o.hora_entrada else "N/A",
            "hora_salida": o.hora_salida.strftime("%H:%M") if o.hora_salida else "PENDIENTE",
            "total": valor_pagar,
            "estado": o.estado,
            "es_amanecida_real": es_amanecida_real
        })
    # --- 2. CONSUMOS ---
    consumo_rows = db.query(Consumo).filter(Consumo.id_arqueo == id_actual).all()
    consumo_patio_list, consumo_hab_list = [], []
    total_consumos_patio = 0.0
    total_consumos_hab = 0.0
    
    for c in consumo_rows:
        total_item = float(c.valor or 0) * (c.cantidad or 1)
        item_data = {
            "id_consumo": c.id_consumo, 
            "fecha": str(c.fecha), 
            "concepto": c.concepto, 
            "cantidad": c.cantidad, 
            "valor": float(c.valor or 0), 
            "total": total_item
        }
        if getattr(c, "id_ocupacion", None):
            total_consumos_hab += total_item
            consumo_hab_list.append(item_data)
        else:
            total_consumos_patio += total_item
            consumo_patio_list.append(item_data)

    # --- 3. COMPRAS PROVEEDOR ---
    compras_rows = db.query(ComprasProveedor).filter(ComprasProveedor.id_arqueo == id_actual).all()
    total_compras_contado, total_compras_credito = 0.0, 0.0
    compras_detalle_list = []
    compras_detalles_planas = [] 

    for comp in compras_rows:
        val_compra = float(comp.total or 0)
        tipo_pago = str(comp.tipo_pago or "contado").lower()
        
        if "credito" in tipo_pago or "crédito" in tipo_pago:
            total_compras_credito += val_compra
        else:
            total_compras_contado += val_compra
        
        prov = db.query(Proveedor).filter(Proveedor.id_proveedor == comp.id_proveedor).first()
        nombre_prov = prov.nombre if prov else "VARIOS"
        
        detalles_db = db.query(CompraDetalle).filter(CompraDetalle.id_compra == comp.id_compra).all()
        
        for d in detalles_db:
            prod_db = db.query(Producto).filter(Producto.id_producto == d.id_producto).first()
            nombre_prod = prod_db.nombre if prod_db else f"ID: {d.id_producto}"
            
            compras_detalles_planas.append({
                "nombre_producto": nombre_prod,
                "nombre_proveedor": nombre_prov,
                "cantidad": d.cantidad,
                "valor": float(d.costo_unitario or 0) * float(d.cantidad or 0),
                "tipo_pago": comp.tipo_pago
            })

    # --- 4. ACPM ---
    acpm_rows = db.query(AcpmLog).filter(AcpmLog.id_arqueo == id_actual).all()
    total_acpm_contado, total_acpm_credito = 0.0, 0.0
    acpm_detalle_list = []

    for a in acpm_rows:
        val = float(a.valor_total or 0)
        acpm_detalle_list.append({
            "fecha": str(a.fecha),
            "proveedor": a.proveedor,
            "litros": a.litros,
            "valor_total": val,
            "tipo_pago": a.tipo_pago
        })
        if "credito" in str(a.tipo_pago or "").lower() or "crédito" in str(a.tipo_pago or "").lower():
            total_acpm_credito += val
        else:
            total_acpm_contado += val

    # --- 5. GASTOS ---
    gastos_rows = db.query(Gasto).filter(Gasto.id_arqueo == id_actual).all()
    total_gastos_contado, total_gastos_credito = 0.0, 0.0
    gastos_detalle_final = []
    
    for g in gastos_rows:
        val = float(g.valor or 0)
        tipo_str = str(g.tipo_pago or "contado").lower()
        
        if "credito" in tipo_str or "crédito" in tipo_str:
            total_gastos_credito += val
        else:
            total_gastos_contado += val

        gastos_detalle_final.append({
            "fecha": str(g.fecha), 
            "concepto": g.concepto, 
            "tipo": g.tipo_pago, 
            "tipo_pago": g.tipo_pago, 
            "valor": val,
            "nombre_proveedor": g.proveedor,
            "proveedor": g.proveedor,
            "cantidad": getattr(g, "cantidad", 1) 
        })

    # --- TOTALES FINALES ---
    total_ventas_final = total_ventas_habitaciones + total_consumos_patio 
    gran_total_credito = total_acpm_credito + total_gastos_credito
    neto = total_ventas_final - total_acpm_contado - total_gastos_contado

    return {
        "ok": True,
        "id_turno": turno.id_arqueo,
        "consecutivo": turno.consecutivo,
        "fecha_inicio": turno.fecha_inicio,
        "fecha_fin": fin,
        "total_ventas": total_ventas_final,
        "cantidad_habitaciones": conteo_habitaciones,
        "suma_solo_habitaciones": total_ventas_habitaciones,
        "ventas_nequi": v_nequi,
        "ventas_datafono": v_datafono,
        "total_credito": gran_total_credito,
        "neto": neto,
        "total_acpm_contado": total_acpm_contado,
        "total_gastos_contado": total_gastos_contado,
        "total_compras_contado": total_compras_contado,
        "total_acpm_credito": total_acpm_credito,
        "total_gastos_credito": total_gastos_credito,
        "total_compras_credito": total_compras_credito,
        "total_consumos_patio": total_consumos_patio, 
        "total_consumos_hab": total_consumos_hab,
        "ventas": ventas_list,
        "habitaciones": ventas_list, # Soporte extra
        "consumos": consumo_patio_list + consumo_hab_list,
        "consumos_hab": consumo_hab_list,
        "gastos": gastos_detalle_final,
        "acpm_detalles": acpm_detalle_list,
        "compras": compras_detalle_list,
        "compras_detalles": compras_detalles_planas  
    }
# ARQUEO DEL DÍA (como lo vienes usando)
# ----------------------------------------------------------
@router.get("/arqueo-dia")
def arqueo_dia(
    fecha: str | None = None,
):
    if fecha:
        fecha_obj = date.fromisoformat(fecha)
    else:
        fecha_obj = datetime.now(COLOMBIA_TZ).date()

    inicio, fin = rango_dia(fecha_obj)

# OCUPACIONES (solo pendientes)
    q_ocup = db.query(Ocupacion).filter(
        Ocupacion.hora_salida != None,
        Ocupacion.total_pagar != None,
        Ocupacion.hora_salida >= inicio,
        Ocupacion.hora_salida <= fin,
        Ocupacion.id_arqueo == None,
    )

    ocupaciones = q_ocup.all()
    habitaciones = {h.id_habitacion: h for h in db.query(tshabitacion).all()}

    ventas_list = []
    total_ventas = 0.0
    for o in ocupaciones:
        hab = habitaciones.get(o.id_habitacion)
        total = float(o.total_pagar or 0)
        ventas_list.append({
            "id_ocupacion": o.id_ocupacion,
            "id_habitacion": o.id_habitacion,
            "numhabitacion": hab.numhabitacion if hab else "",
            "hora_entrada": o.hora_entrada,
            "hora_salida": o.hora_salida,
            "total": total,
        })
        total_ventas += total

# ACPM (solo pendientes)
    q_acpm = db.query(AcpmLog).filter(
        AcpmLog.fecha == fecha_obj,
        AcpmLog.id_arqueo == None
    )

    acpm_rows = q_acpm.all()
    acpm_list = []
    total_acpm_contado = 0.0
    total_acpm_credito = 0.0

    for a in acpm_rows:
        val = float(a.valor_total or 0)
        tipo = getattr(a, "tipo_pago", "contado") or "contado"
        es_credito = str(tipo).lower() == "credito"

        acpm_list.append({
            "id_acpm": a.id_acpm,
            "fecha": a.fecha,
            "litros": float(a.litros or 0),
            "valor_total": val,
            "proveedor": a.proveedor,
            "tipo_pago": tipo,
        })

        if es_credito:
            total_acpm_credito += val
        else:
            total_acpm_contado += val

# GASTOS (solo pendientes)
    q_gastos = db.query(Gasto).filter(
        Gasto.fecha == fecha_obj,
        Gasto.id_arqueo == None
    )

    gastos_rows = q_gastos.all()
    gastos_list = []
    total_gastos_contado = 0.0
    total_gastos_credito = 0.0

    for g in gastos_rows:
        val = float(g.valor or 0)
        tipo = getattr(g, "tipo_pago", "contado") or "contado"
        es_credito = str(tipo).lower() == "credito"

        gastos_list.append({
            "id_gasto": g.id_gasto,
            "fecha": g.fecha,
            "concepto": g.concepto,
            "valor": val,
            "proveedor": g.proveedor,
            "nota": g.nota,
            "tipo_pago": tipo,
        })

        if es_credito:
            total_gastos_credito += val
        else:
            total_gastos_contado += val

# CONSUMOS (solo pendientes)
    q_consumos = db.query(Consumo).filter(
        Consumo.fecha == fecha_obj,
        Consumo.id_arqueo == None
    )

    consumo_rows = q_consumos.all()
    consumo_list = []
    total_consumos = 0.0

    for c in consumo_rows:
        total_item = float(c.valor or 0) * (c.cantidad or 1)
        total_consumos += total_item
        consumo_list.append({
            "id_consumo": c.id_consumo,
            "fecha": c.fecha,
            "concepto": c.concepto,
            "cantidad": c.cantidad,
            "valor": float(c.valor or 0),
            "total": total_item,
            "nota": c.nota,
        })

    neto = total_ventas + total_consumos - total_acpm_contado - total_gastos_contado

    return {
        "fecha": fecha_obj,
        "total_ventas": total_ventas,
        "total_acpm_contado": total_acpm_contado,
        "total_acpm_credito": total_acpm_credito,
        "total_gastos_contado": total_gastos_contado,
        "total_gastos_credito": total_gastos_credito,
        "total_consumos": total_consumos,
        "neto": neto,
        "ventas": ventas_list,
        "acpm": acpm_list,
        "gastos": gastos_list,
        "consumos": consumo_list,
    }

# ----------------------------------------------------------
# ✅ CERRAR TURNO REAL
# POST /dashboard/arqueo/cerrar-turno
# ----------------------------------------------------------
# ----------------------------------------------------------
@router.post("/arqueo/cerrar-turno")
def cerrar_turno(db: Session = Depends(get_db)):
    turno = obtener_turno_activo(db)
    if not turno:
        turno = asegurar_turno_activo(db)
        return {"ok": True, "message": "Se creó un turno activo nuevo", "id_turno": turno.id_arqueo}

    fin = ahora_co()
    # 1. Obtenemos los cálculos actuales
    resumen = arqueo_turno_activo(db=db)

    # ✅ ACTUALIZACIÓN DE CABECERA
    turno.fecha_fin = fin
    turno.total_ventas = resumen["total_ventas"]
    turno.total_acpm = resumen["total_acpm_contado"]
    turno.total_gastos = resumen["total_gastos_contado"]
    turno.total_consumos = resumen["total_consumos_patio"] + resumen["total_consumos_hab"]
    turno.neto = resumen["neto"]

    # GUARDAR DESGLOSES EN LA DB
    turno.ventas_nequi = resumen.get("ventas_nequi", 0)
    turno.ventas_datafono = resumen.get("ventas_datafono", 0)
    turno.total_acpm_credito = resumen.get("total_acpm_credito", 0)
    turno.total_gastos_credito = resumen.get("total_gastos_credito", 0)
    turno.total_compras_credito = resumen.get("total_compras_credito", 0)

    db.commit()

    # ✅ VINCULACIÓN DE MOVIMIENTOS (Ajustado para usar Timestamp exacto)
    inicio_turno = turno.fecha_inicio

    # 1. Habitaciones (Ya estaba bien)
    db.query(Ocupacion).filter(
        Ocupacion.id_arqueo == None,
        Ocupacion.hora_salida >= inicio_turno,
        Ocupacion.hora_salida <= fin
    ).update({Ocupacion.id_arqueo: turno.id_arqueo}, synchronize_session=False)

    # 2. ACPM (Cambiado de func.date a comparación directa de fecha/hora)
    db.query(AcpmLog).filter(
        AcpmLog.id_arqueo == None,
        AcpmLog.fecha >= inicio_turno,
        AcpmLog.fecha <= fin
    ).update({AcpmLog.id_arqueo: turno.id_arqueo}, synchronize_session=False)

    # 3. Gastos
    db.query(Gasto).filter(
        Gasto.id_arqueo == None,
        Gasto.fecha >= inicio_turno,
        Gasto.fecha <= fin
    ).update({Gasto.id_arqueo: turno.id_arqueo}, synchronize_session=False)

    # 4. Consumos
    db.query(Consumo).filter(
        Consumo.id_arqueo == None,
        Consumo.fecha >= inicio_turno,
        Consumo.fecha <= fin
    ).update({Consumo.id_arqueo: turno.id_arqueo}, synchronize_session=False)

    # 5. Compras
    db.query(ComprasProveedor).filter(
        ComprasProveedor.id_arqueo == None,
        ComprasProveedor.fecha >= inicio_turno,
        ComprasProveedor.fecha <= fin
    ).update({ComprasProveedor.id_arqueo: turno.id_arqueo}, synchronize_session=False)

    # 🔥 MUY IMPORTANTE: Commit aquí para asegurar que los IDs de arqueo se graben
    db.commit()

    # 2. Ahora sí pedimos los detalles, que ya están vinculados
    detalles = detalle_arqueo(id_arqueo=turno.id_arqueo, db=db)

    # 3. Paquete para la tirilla
    resumen_para_tirilla = {
        **detalles,
        "ventas_nequi": float(resumen.get("ventas_nequi", 0)),
        "ventas_datafono": float(resumen.get("ventas_datafono", 0)),
        "total_acpm_credito": float(resumen.get("total_acpm_credito", 0)),
        "total_gastos_credito": float(resumen.get("total_gastos_credito", 0)),
        "total_compras": float(resumen.get("total_compras_contado", 0)),
        "total_compras_credito": float(resumen.get("total_compras_credito", 0)),
        "total_ventas": float(resumen.get("total_ventas", 0)),
        "neto": float(resumen.get("neto", 0)),

        "consumos": resumen.get("consumos", []),      # Lista ya filtrada solo para patio
        "consumos_hab": resumen.get("consumos_hab", []) # Lista ya filtrada solo para hab
    



    }

    # ✅ CREAR NUEVO TURNO
    nuevo = ArqueoTurno(
        consecutivo=(turno.consecutivo or 0) + 1,
        fecha_inicio=ahora_co(),
        fecha_fin=None,
        total_ventas=0,
        total_acpm=0,
        total_gastos=0,
        total_consumos=0,
        neto=0,
    )
    db.add(nuevo)
    db.commit()

    return {
        "ok": True,
        "message": "Turno cerrado correctamente",
        "id_turno_cerrado": turno.id_arqueo,
        "resumen": resumen_para_tirilla
    }
# ----------------------------------------------------------
# ✅ ALIAS para que tu Front NO dé 404
# POST /dashboard/arqueo-dia/cerrar
# ----------------------------------------------------------
@router.post("/arqueo-dia/cerrar")
def cerrar_turno_alias(db: Session = Depends(get_db)):
    return cerrar_turno(db=db)







# ----------------------------------------------------------
# ✅ RUTA PARA CARGAR PRECIOS ACTUALES (HABITACIONES ACTIVAS)
# GET /dashboard/ocupaciones/activas
# ----------------------------------------------------------
# --- REEMPLAZA ESTA FUNCIÓN AL FINAL DE TU dashboard.py ---

@router.get("/ocupaciones/activas")
def obtener_ocupaciones_activas(db: Session = Depends(get_db)):
    # Buscamos ocupaciones donde hora_salida sea NULL (es decir, están adentro)
    activas = db.query(Ocupacion).filter(Ocupacion.hora_salida == None).all()
    
    resultado = []
    for o in activas:
        # Si es amanecida, el precio ya está en total_pagar (los 57.000)
        # Si es normal, total_pagar será 0 o None hasta que salgan
        precio_mostrado = float(o.total_pagar or 0)
        
        resultado.append({
            "id_ocupacion": o.id_ocupacion,
            "id_habitacion": o.id_habitacion,
            "total_pagar": precio_mostrado,
            "observaciones": o.observaciones,
            "estado": o.estado
        })
    
    return resultado

# ----------------------------------------------------------
# 📊 REPORTE DIARIO (AGRUPADO POR DÍA)
# GET /dashboard/reportes/diario
# ----------------------------------------------------------
@router.get("/reportes/diario")
def reporte_diario(
    desde: str | None = None,
    hasta: str | None = None,
    db: Session = Depends(get_db),
):
# fechas
    if desde:
        fecha_desde = date.fromisoformat(desde)
    else:
        fecha_desde = date.today() - timedelta(days=7)

    if hasta:
        fecha_hasta = date.fromisoformat(hasta)
    else:
        fecha_hasta = date.today()

    rows = (
        db.query(
            func.date(ArqueoTurno.fecha_inicio).label("fecha"),
            func.sum(ArqueoTurno.total_ventas).label("ventas"),
            func.sum(ArqueoTurno.total_consumos).label("consumos"),
            func.sum(ArqueoTurno.total_gastos).label("gastos"),
            func.sum(ArqueoTurno.total_acpm).label("acpm"),
            func.sum(ArqueoTurno.neto).label("neto"),
        )
        .filter(
            ArqueoTurno.fecha_fin != None,
            func.date(ArqueoTurno.fecha_inicio) >= fecha_desde,
            func.date(ArqueoTurno.fecha_inicio) <= fecha_hasta,
        )
        .group_by(func.date(ArqueoTurno.fecha_inicio))
        .order_by(func.date(ArqueoTurno.fecha_inicio))
        .all()
    )

    data = []
    for r in rows:
        data.append({
            "fecha": r.fecha.isoformat(),
            "ventas": float(r.ventas or 0),
            "consumos": float(r.consumos or 0),
            "gastos": float(r.gastos or 0),
            "acpm": float(r.acpm or 0),
            "neto": float(r.neto or 0),
        })

    return {
        "desde": fecha_desde,
        "hasta": fecha_hasta,
        "data": data,
    }
