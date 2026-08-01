from sqlalchemy import Column, Integer
from dependencies.database import Base

class Inventario(Base):
    __tablename__ = "inventario"

    id_producto = Column(Integer, primary_key=True)
    stock = Column(Integer, nullable=False, default=0)
