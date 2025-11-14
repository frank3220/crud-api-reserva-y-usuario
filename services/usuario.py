from sqlalchemy.orm import Session
from schemas.usuario import UsuarioCreate
from repositories.usuario import UsuarioRepository # Importa la clase del Repositorio

class UsuarioService:
    def __init__(self, db: Session):
        """Inicializa el servicio con el repositorio de usuarios."""
        self.repo = UsuarioRepository(db) 

    def create_usuario(self, usuario_in: UsuarioCreate):
        """Llama al repositorio para crear un usuario, el repositorio maneja el hashing."""
        return self.repo.create(usuario_in)
    
    def get_usuario_by_email(self, email: str):
        """Obtiene un usuario por email."""
        return self.repo.get_by_email(email)

    def get_usuario_by_id(self, usuario_id: int):
        """Obtiene un usuario por ID."""
        return self.repo.get_by_id(usuario_id)

    def get_all_usuarios(self, skip: int = 0, limit: int = 100):
        """Obtiene todos los usuarios."""
        return self.repo.get_all(skip=skip, limit=limit)