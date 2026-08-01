from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from dependencies.database import get_db
from models.room import tshabitacion
from models.ocupacion import Ocupacion
from services.arqueo import ArqueoService # Asegúrate de tener esta importación arriba

router_dashboard = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# ---------------------------------------------------------
# MÉTRICAS DEL DASHBOARD (Tu código original)
# ---------------------------------------------------------
@router_dashboard.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    try:
        total_habs = db.query(tshabitacion).count()
        ocupadas = db.query(Ocupacion).filter(Ocupacion.hora_salida == None).count()

        return {
            "totalReservas": 0,
            "clientesNuevos": 0,
            "ingresosMes": 0,
            "ocupacion": (ocupadas / total_habs * 100) if total_habs > 0 else 0
        }
    except Exception as e:
        return {"totalReservas": 0, "clientesNuevos": 0, "ingresosMes": 0, "ocupacion": 0}

# ---------------------------------------------------------
# ESTADO DE HABITACIONES (Tu código original)
# ---------------------------------------------------------
@router_dashboard.get("/rooms-status")
def get_rooms_status(db: Session = Depends(get_db)):
    habitaciones = db.query(tshabitacion).all()
    data = []
    for h in habitaciones:
        data.append({
            "id": h.id_habitacion,
            "numero": h.numhabitacion,
            "estado": "ocupada" if h.ocupada else "libre",
            "precio": h.precio
        })
    return {"habitaciones": data}

@router_dashboard.get("/rooms")
def get_rooms(db: Session = Depends(get_db)):
    habitaciones = db.query(tshabitacion).all()
    return [
        {"id": h.id_habitacion, "numero": h.numhabitacion, "estado": h.estado, "precio": h.precio}
        for h in habitaciones
    ]

# ---------------------------------------------------------
# ARQUEOS Y REPORTES (CORREGIDO PARA TU DB REAL)
# ---------------------------------------------------------

@router_dashboard.get("/arqueos/fecha/{fecha}")
def buscar_arqueos_por_fecha(fecha: str, db: Session = Depends(get_db)):
    # Usamos creado_en que es la columna que veo en tus fotos
    query = text("SELECT * FROM tsarqueo_turno WHERE DATE(creado_en) = :f")
    result = db.execute(query, {"f": fecha}).mappings().all()
    return [dict(row) for row in result]

from services.arqueo import ArqueoService # Asegúrate de tener esta importación arriba

@router_dashboard.get("/arqueos/detalle/{id_arqueo}")
def obtener_detalle_cierre(id_arqueo: int, db: Session = Depends(get_db)):
    service = ArqueoService(db)
    resultado = service.obtener_detalle_arqueos(id_arqueo)
    
    if not resultado:
        return {"habitaciones": [], "gastos": [], "acpm": [], "detalles": []}

    # 🚨 EXTRACCIÓN Y LIMPIEZA DE HABITACIONES
    lista_habs_raw = resultado.get("habitaciones", [])
    lista_habs_procesada = []

    for h in lista_habs_raw:
        # Intentamos obtener valores clave para identificar la transacción
        tipo_servicio = str(h.get("tipo") or h.get("concepto") or h.get("tipo_servicio") or "").lower()
        descripcion_servicio = str(h.get("descripcion") or h.get("tarifa") or "").lower()
        
        total_pago = float(h.get("total") or h.get("valor") or 0)
        valor_base = float(h.get("valor_estadia") or h.get("precio_base") or total_pago)

        # 🧠 DETECTOR INTELIGENTE DE AMANECIDA:
        # Condición 1: El texto explícitamente dice amanecida
        es_amanecida_texto = "amanec" in tipo_servicio or "amanec" in descripcion_servicio or h.get("es_amanecida") in [True, "true", 1, "1"]

        # Condición 2: El valor base o total encaja con tus tarifas de amanecida ($57k, $70k, $90k, etc.)
        # Excluye tajantemente los cobros de ratos por horas ($25.000, $30.000, $42.000)
        es_tarifa_amanecida_precio = (valor_base >= 45000) and not ("rato" in tipo_servicio or "hora" in tipo_servicio)

        # Si cumple cualquiera de las dos, le clavamos la bandera Verdadera al Frontend
        h["es_amanecida_real"] = True if (es_amanecida_texto or es_tarifa_amanecida_precio) else False
        
        lista_habs_procesada.append(h)

    # --- RETORNAMOS TODO EL DICCIONARIO PERFECTO ---
    return {
        "resumen": {
            "id_arqueo": resultado.get("id_arqueo"),
            "consecutivo": resultado.get("consecutivo"),
            "total_ventas": resultado.get("total_ventas"),
            "neto": resultado.get("neto"),
            "fecha_inicio": resultado.get("fecha_inicio"),
            "fecha_fin": resultado.get("fecha_fin"),
            "ventas_nequi": resultado.get("ventas_nequi", 0),
            "ventas_datafono": resultado.get("ventas_datafono", 0),
            "total_acpm_contado": resultado.get("total_acpm_contado", 0),
            "total_acpm_credito": resultado.get("total_acpm_credito", 0),
            "total_gastos_contado": resultado.get("total_gastos_contado", 0),
            "total_gastos_credito": resultado.get("total_gastos_credito", 0),
            "total_compras_contado": resultado.get("total_compras_contado", 0),
            "total_compras_credito": resultado.get("total_compras_credito", 0),
            "suma_solo_habitaciones": resultado.get("suma_solo_habitaciones", 0)
        },
        "detalles": resultado.get("detalles", []),
        "habitaciones": lista_habs_procesada,  # 🔥 Aquí inyectamos la lista con la propiedad blindada
        "ventas": lista_habs_procesada,       # Doble mapeo por si el frontend lee det.ventas
        "gastos": resultado.get("gastos", []),
        "acpm": resultado.get("acpm_detalles", [])
    }