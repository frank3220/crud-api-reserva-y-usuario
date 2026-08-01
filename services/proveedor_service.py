from sqlalchemy.orm import Session
from models.proveedor import Proveedor
from schemas.proveedor_schema import ProveedorCreate, ProveedorUpdate


class ProveedorService:
    def __init__(self, db: Session):
        self.db = db

    def listar(self):
        return self.db.query(Proveedor).order_by(Proveedor.nombre).all()

    def crear(self, data: ProveedorCreate):
        proveedor = Proveedor(**data.dict())
        self.db.add(proveedor)
        self.db.commit()
        self.db.refresh(proveedor)
        return proveedor

    def actualizar(self, id_proveedor: int, data: ProveedorUpdate):
        proveedor = self.db.get(Proveedor, id_proveedor)
        if not proveedor:
            return None

        for k, v in data.dict(exclude_unset=True).items():
            setattr(proveedor, k, v)

        self.db.commit()
        self.db.refresh(proveedor)
        return proveedor

    def toggle_activo(self, id_proveedor: int):
        proveedor = self.db.get(Proveedor, id_proveedor)
        if not proveedor:
            return None

        proveedor.activo = not proveedor.activo
        self.db.commit()
        self.db.refresh(proveedor)
        return proveedor
