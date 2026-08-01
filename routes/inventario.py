from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.database import get_db
from models.producto import Producto
from models.inventario import Inventario

router = APIRouter(
    prefix="/inventario",
    tags=["Inventario"],
)

# ============================================================
# 🟢 INVENTARIO PARA PATIO
# Muestra productos + stock real
# ============================================================
@router.get("/patio")
def inventario_patio(db: Session = Depends(get_db)):
    """
    Devuelve el inventario REAL para consumo en patio.
    Incluye:
    - id_producto
    - nombre
    - precio
    - stock actual
    """

    rows = (
        db.query(
            Producto.id_producto,
            Producto.nombre,
            Producto.precio,
            Inventario.stock,
        )
        .outerjoin(
            Inventario,
            Inventario.id_producto == Producto.id_producto,
        )
        .filter(Producto.activo == True)
        .order_by(Producto.nombre.asc())
        .all()
    )

    resultado = []
    for r in rows:
        resultado.append({
            "id_producto": r.id_producto,
            "nombre": r.nombre,
            "precio": float(r.precio or 0),
            "stock": int(r.stock or 0),  # 🔥 si no hay inventario, muestra 0
        })

    return resultado
