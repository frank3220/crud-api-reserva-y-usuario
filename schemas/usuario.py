from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str
    email: str
    rol: str

class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=8)

class UsuarioUpdate(UsuarioBase):
    nombre: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)

class Usuario(UsuarioBase):
    idusuario: int # CRÍTICO: Asegúrate de que este nombre coincida con la clave primaria en models/usuario.py

    # ✅ CORRECCIÓN: Usamos la configuración moderna (Pydantic V2)
    model_config = ConfigDict(from_attributes=True)
