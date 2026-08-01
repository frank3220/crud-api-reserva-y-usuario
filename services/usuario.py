from fastapi import HTTPException
from sqlalchemy.orm import Session

from repositories.usuario import UsuarioRepository
from schemas.usuario import UsuarioCreate
from utils.security import create_access_token, verify_password


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UsuarioRepository(db)

    def create_usuario(
        self,
        usuario_in: UsuarioCreate,
        company_id: int | None = None,
        motel_id: int | None = None,
    ):
        return self.repo.create(usuario_in, company_id=company_id, motel_id=motel_id)

    def get_usuario_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def get_usuario_by_id(
        self,
        usuario_id: int,
        company_id: int | None = None,
        motel_id: int | None = None,
    ):
        return self.repo.get_by_id(usuario_id, company_id=company_id, motel_id=motel_id)

    def get_all_usuarios(
        self,
        skip: int = 0,
        limit: int = 100,
        company_id: int | None = None,
        motel_id: int | None = None,
    ):
        return self.repo.get_all(skip=skip, limit=limit, company_id=company_id, motel_id=motel_id)

    def login(self, email: str, password: str):
        usuario = self.repo.get_by_email(email)
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        if getattr(usuario, "activo", True) is False:
            raise HTTPException(status_code=403, detail="Usuario inactivo")
        if not verify_password(password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        token = create_access_token({
            "sub": str(usuario.idusuario),
            "rol": usuario.rol.upper() if usuario.rol else "CAJERO",
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.idusuario,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "rol": usuario.rol.upper() if usuario.rol else "CAJERO",
                "tiene_turno_abierto": False,
            },
        }
