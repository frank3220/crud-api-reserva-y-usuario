from sqlalchemy.orm import Session
from sqlalchemy import outerjoin

from models.producto import Producto
from models.inventario import Inventario
from schemas.producto_schema import ProductoCreate, ProductoUpdate


class ProductoService:
    def __init__(self, db: Session):
        self.db = db

    # 🔹 listar productos activos CON STOCK
    def listar(self):
        resultados = (
            self.db.query(
                Producto,
                Inventario.stock
            )
            .outerjoin(
                Inventario,
                Inventario.id_producto == Producto.id_producto
            )
            .filter(Producto.activo == True)
            .all()
        )

        productos = []
        for prod, stock in resultados:
            prod_dict = prod.__dict__.copy()
            prod_dict["stock"] = stock or 0  # 🔥 CLAVE
            prod_dict.pop("_sa_instance_state", None)
            productos.append(prod_dict)

        return productos

    # 🔹 crear producto
    def crear(self, data: ProductoCreate):
        prod = Producto(
            nombre=data.nombre,
            precio=data.precio
        )
        self.db.add(prod)
        self.db.commit()
        self.db.refresh(prod)

        # 🔥 crear registro de inventario automáticamente
        inv = Inventario(
            id_producto=prod.id_producto,
            stock=0
        )
        self.db.add(inv)
        self.db.commit()

        return prod

    # ✏️ editar producto
    def actualizar(self, id_producto: int, data: ProductoUpdate):
        producto = self.db.query(Producto).get(id_producto)
        if not producto:
            return None

        producto.nombre = data.nombre
        producto.precio = data.precio
        self.db.commit()
        return producto

    # 🟢🔴 activar / desactivar producto
    def cambiar_estado(self, id_producto: int):
        producto = self.db.query(Producto).get(id_producto)
        if not producto:
            return None

        producto.activo = not producto.activo
        self.db.commit()
        return producto
