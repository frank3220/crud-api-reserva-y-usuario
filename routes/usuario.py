from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importaciones de tu estructura de carpetas
from dependencies.database import get_db
from schemas.usuario import UsuarioCreate, Usuario
from services.usuario import UsuarioService

router = APIRouter(tags=["Usuarios"])

def get_service(db: Session = Depends(get_db)):
    return UsuarioService(db)

# ===============================
# LOGIN
# ===============================
@router.post("/auth/login")
def login(email: str, password: str, service: UsuarioService = Depends(get_service)):
    # Llama a tu lógica de service que ya genera el token JWT y el rol
    return service.login(email, password)

# ===============================
# GESTIÓN DE PERSONAL (CRUD)
# ===============================

@router.get("/api/v1/usuarios", response_model=List[Usuario])
def listar_usuarios(service: UsuarioService = Depends(get_service)):
    """ Trae la lista de empleados para la tabla """
    return service.get_all_usuarios()

@router.post("/api/v1/usuarios", response_model=Usuario)
def crear_usuario(usuario: UsuarioCreate, service: UsuarioService = Depends(get_service)):
    """ Registra un nuevo empleado """
    db_user = service.get_usuario_by_email(usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    return service.create_usuario(usuario)

@router.delete("/api/v1/usuarios/{usuario_id}")
def eliminar_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db), 
    service: UsuarioService = Depends(get_service)
):
    """
    Busca y elimina al usuario directamente usando la base de datos
    """
    # 1. Buscamos al usuario usando el ID (asegúrate que en tu service se llame get_usuario_by_id)
    user = service.get_usuario_by_id(usuario_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        # 2. Ejecutamos el borrado físico en la DB
        db.delete(user)
        db.commit()
        return {"detail": "Usuario eliminado correctamente"}
    except Exception as e:
        db.rollback()
        print(f"ERROR AL ELIMINAR: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar")