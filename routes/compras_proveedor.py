from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from dependencies.database import get_db
from schemas.compras_proveedor import CompraProveedorCreate

from models.compras_proveedor import ComprasProveedor
from models.compra_detalle import CompraDetalle
from models.inventario import Inventario
from models.proveedor import Proveedor
from models.arqueo import ArqueoTurno
from models.gastos import Gasto  # ✅ IMPORTANTE para reflejar en panel "Gastos"

router = APIRouter(
    prefix="/compras-proveedor",
    tags=["Compras Proveedor"]
)


def _normalizar_tipo_pago(tipo: str) -> str:
    t = (tipo or "").strip().lower()
    t = t.replace("crédito", "credito")
    if t not in ("contado", "credito"):
        t = "contado"
    return t


@router.post("/")
def crear_compra_proveedor(
    data: CompraProveedorCreate,
    db: Session = Depends(get_db)
):
    try:
        tipo_pago = _normalizar_tipo_pago(data.tipo_pago)

        proveedor = (
            db.query(Proveedor)
            .filter(Proveedor.id_proveedor == data.id_proveedor)
            .first()
        )
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        # 🔑 TOMAR TURNO ACTIVO
        turno = (
            db.query(ArqueoTurno)
            .filter(ArqueoTurno.fecha_fin == None)
            .order_by(ArqueoTurno.id_arqueo.desc())
            .first()
        )

        if not turno:
            raise HTTPException(status_code=400, detail="No hay un turno activo")

        # ✅ FECHA FIJA = FECHA DEL TURNO (para no brincar de día)
        fecha_compra = turno.fecha_inicio.date()

        # ✅ Crear encabezado de compra
        compra = ComprasProveedor(
            id_proveedor=data.id_proveedor,
            fecha=fecha_compra,
            tipo_pago=tipo_pago,
            nota=data.nota,
            total=0,
            # 🔥 CAMBIO CLAVE: Asignamos el ID del arqueo de una vez
            id_arqueo=turno.id_arqueo,  
        )

        db.add(compra)
        db.flush()  # para obtener id_compra

        total_compra = 0.0

        # ✅ Guardar detalles + aumentar inventario
        for d in data.detalles:
            subtotal = float(d.cantidad) * float(d.costo_unitario)
            total_compra += subtotal

            detalle = CompraDetalle(
                id_compra=compra.id_compra,
                id_producto=d.id_producto,
                cantidad=d.cantidad,
                costo_unitario=d.costo_unitario
            )
            db.add(detalle)

            inv = (
                db.query(Inventario)
                .filter(Inventario.id_producto == d.id_producto)
                .first()
            )

            if inv:
                inv.stock = (inv.stock or 0) + int(d.cantidad)
            else:
                db.add(
                    Inventario(
                        id_producto=d.id_producto,
                        stock=int(d.cantidad)
                    )
                )

        compra.total = float(total_compra)

        # ✅ SI ES CONTADO => SE REGISTRA COMO GASTO (para que aparezca en panel)
        if tipo_pago == "contado":
            gasto = Gasto(
                fecha=fecha_compra,
                concepto=f"Compra proveedor: {proveedor.nombre}",
                valor=float(total_compra),
                proveedor=proveedor.nombre,
                nota=data.nota,
                tipo_pago="contado",
                # 🔥 CAMBIO CLAVE: También asignamos el ID al gasto
                id_arqueo=turno.id_arqueo  
            )
            db.add(gasto)

        db.commit()

        return {
            "message": "Compra registrada correctamente",
            "id_compra": compra.id_compra,
            "total": float(total_compra),
            "tipo_pago": tipo_pago,
            "fecha": str(fecha_compra),
        }

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as e:
        db.rollback()
        print("🔥 ERROR SQL COMPRA PROVEEDOR:", str(e))
        raise HTTPException(status_code=500, detail="Error en base de datos")

    except Exception as e:
        db.rollback()
        print("🔥 ERROR GENERAL COMPRA PROVEEDOR:", str(e))
        raise HTTPException(status_code=500, detail="Error interno")