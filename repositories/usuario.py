from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.usuario import Usuario as UsuarioModel
from schemas.usuario import UsuarioCreate
from utils.security import hash_password


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        usuario: UsuarioCreate,
        company_id: int | None = None,
        motel_id: int | None = None,
    ) -> UsuarioModel:
        db_usuario = UsuarioModel(
            email=usuario.email,
            nombre=usuario.nombre,
            password_hash=hash_password(usuario.password),
            rol=usuario.rol,
            id_company=company_id or 1,
            id_motel=motel_id or 1,
        )

        try:
            self.db.add(db_usuario)
            self.db.commit()
            self.db.refresh(db_usuario)
            return db_usuario
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya esta registrado. Utiliza otro email.",
            )
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error inesperado al crear el usuario.",
            )

    def get_by_email(self, email: str) -> UsuarioModel | None:
        return self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: int | None = None,
        motel_id: int | None = None,
    ):
        query = self.db.query(UsuarioModel)
        if company_id is not None:
            query = query.filter(UsuarioModel.id_company == company_id)
        if motel_id is not None:
            query = query.filter(UsuarioModel.id_motel == motel_id)
        return query.offset(skip).limit(limit).all()

    def get_by_id(
        self,
        id: int,
        company_id: int | None = None,
        motel_id: int | None = None,
    ) -> UsuarioModel | None:
        query = self.db.query(UsuarioModel).filter(UsuarioModel.idusuario == id)
        if company_id is not None:
            query = query.filter(UsuarioModel.id_company == company_id)
        if motel_id is not None:
            query = query.filter(UsuarioModel.id_motel == motel_id)
        return query.first()
