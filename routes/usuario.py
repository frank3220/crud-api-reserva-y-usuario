from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas.usuario import UsuarioCreate, Usuario # Esquemas para entrada/salida
from services.usuario import UsuarioService # Importa la clase de servicio
from typing import List

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])

# Dependencia para obtener la sesión de DB y crear el servicio
def get_service(db: Session = Depends(get_db)):
    """Inyecta la instancia del servicio de usuario."""
    return UsuarioService(db)

@router.post("/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
def create_usuario_route(
    usuario_in: UsuarioCreate,
    service: UsuarioService = Depends(get_service) # Inyecta el servicio
):
    """
    Crea un nuevo usuario en la base de datos.
    """
    # El servicio/repositorio maneja el hashing de la contraseña y las excepciones
    try:
        new_user = service.create_usuario(usuario_in)
        return new_user
    except HTTPException as e:
        # Re-lanza la excepción (ej. 400 por email duplicado desde el repositorio)
        raise e

@router.get("/", response_model=List[Usuario])
def read_usuarios_route(service: UsuarioService = Depends(get_service)):
    """
    Obtiene todos los usuarios.
    """
    return service.get_all_usuarios()

@router.get("/{usuario_id}", response_model=Usuario)
def read_usuario_by_id_route(usuario_id: int, service: UsuarioService = Depends(get_service)):
    """
    Obtiene un usuario por su ID.
    """
    db_usuario = service.get_usuario_by_id(usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

# Nota: Puedes añadir aquí las rutas de PUT y DELETE si las necesitas.