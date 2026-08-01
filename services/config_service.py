from sqlalchemy.orm import Session
from models.configuracion import Configuracion
from fastapi import HTTPException


class ConfigService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, clave: str, default=None):
        """
        Obtiene un valor desde la tabla configuracion.
        Los valores siempre se almacenan como texto,
        así que aquí convertimos a int cuando corresponde.
        """
        item = (
            self.db.query(Configuracion)
            .filter(Configuracion.clave == clave)
            .first()
        )

        if not item:
            return default

        valor = item.valor

        # Intentar castear a número si corresponde
        try:
            return int(valor)
        except:
            return valor  # Retorna texto si no es número

    def set(self, clave: str, valor):
        """
        Guarda o actualiza un valor de configuración.
        Se almacena como TEXTO siempre.
        """
        item = (
            self.db.query(Configuracion)
            .filter(Configuracion.clave == clave)
            .first()
        )

        valor = str(valor)  # Forzar que todo se guarde como string

        if item:
            item.valor = valor
        else:
            item = Configuracion(clave=clave, valor=valor)
            self.db.add(item)

        self.db.commit()
        self.db.refresh(item)
        return item
