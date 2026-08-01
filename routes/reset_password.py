from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import argon2
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from dependencies.database import get_db
from models.usuario import Usuario
from utils.security import RoleChecker


router = APIRouter(tags=["Usuarios"])
ADMIN_ROLES = ["ADMIN", "ADMINISTRADOR", "SUPER_ADMIN", "DUEÑO", "DUENO"]


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(min_length=8)


@router.patch("/reset-password/{user_id}")
def reset_password(
    user_id: int,
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
    _admin=Depends(RoleChecker(ADMIN_ROLES)),
):
    user = (
        db.query(Usuario)
        .filter(
            Usuario.idusuario == user_id,
            Usuario.id_company == (getattr(_admin, "id_company", None) or 1),
            Usuario.id_motel == (getattr(_admin, "id_motel", None) or 1),
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.password_hash = argon2.hash(body.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "status": "ok",
        "message": f"Contraseña actualizada para usuario ID {user_id}",
    }
