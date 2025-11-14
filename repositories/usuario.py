from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.usuario import Usuario as UsuarioModel
from schemas.usuario import UsuarioCreate
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

# Usamos Argon2 para evitar conflictos de bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Función para obtener el hash de la contraseña
def get_password_hash(password: str) -> str:
    """
    Hashea la contraseña usando Argon2.
    """
    return pwd_context.hash(password)

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, usuario: UsuarioCreate) -> UsuarioModel:
        """Crea un nuevo usuario y hashea la contraseña."""
        
        hashed_password = get_password_hash(usuario.password)

        db_usuario = UsuarioModel(
            email=usuario.email,
            nombre=usuario.nombre,
            # *** CORRECCIÓN: Usamos 'password_hash' en lugar de 'password' ***
            password_hash=hashed_password, 
            # *******************************************************************
            rol=usuario.rol 
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
                detail="El email ya está registrado. Utiliza otro email."
            )
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado al crear el usuario: {e}"
            )

    def get_by_email(self, email: str) -> UsuarioModel | None:
        """Obtiene un usuario por su email."""
        return self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        """Obtiene todos los usuarios con paginación."""
        return self.db.query(UsuarioModel).offset(skip).limit(limit).all()

    def get_by_id(self, id: int) -> UsuarioModel | None:
        """Obtiene un usuario por su ID."""
        return self.db.query(UsuarioModel).filter(UsuarioModel.idusuario == id).first()