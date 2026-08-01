from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dependencies.database import get_db
from schemas.usuario import UsuarioCreate
from services.usuario import UsuarioService
from utils.security import RoleChecker


router = APIRouter(prefix="/auth", tags=["Auth"])
ADMIN_ROLES = ["ADMIN", "ADMINISTRADOR", "SUPER_ADMIN", "DUEÑO", "DUENO"]
MAX_LOGIN_ATTEMPTS = 8
LOGIN_WINDOW_SECONDS = 300
LOGIN_LOCK_SECONDS = 600
_login_attempts: dict[str, dict[str, float | int]] = {}


class LoginRequest(BaseModel):
    email: str
    password: str


def get_service(db: Session = Depends(get_db)):
    return UsuarioService(db)


def _login_key(request: Request, email: str) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip = forwarded_for.split(",", 1)[0].strip() if forwarded_for else ""
    if not ip and request.client:
        ip = request.client.host
    return f"{ip or 'unknown'}:{email.strip().lower()}"


def _assert_login_not_locked(key: str) -> None:
    now = monotonic()
    data = _login_attempts.get(key)
    if not data:
        return
    locked_until = float(data.get("locked_until") or 0)
    if locked_until and now < locked_until:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Intenta de nuevo en unos minutos.",
        )
    first_attempt_at = float(data.get("first_attempt_at") or now)
    if now - first_attempt_at > LOGIN_WINDOW_SECONDS:
        _login_attempts.pop(key, None)


def _record_failed_login(key: str) -> None:
    now = monotonic()
    data = _login_attempts.get(key)
    if not data or now - float(data.get("first_attempt_at") or now) > LOGIN_WINDOW_SECONDS:
        data = {"count": 0, "first_attempt_at": now, "locked_until": 0}
    data["count"] = int(data.get("count") or 0) + 1
    if int(data["count"]) >= MAX_LOGIN_ATTEMPTS:
        data["locked_until"] = now + LOGIN_LOCK_SECONDS
    _login_attempts[key] = data


def _clear_failed_login(key: str) -> None:
    _login_attempts.pop(key, None)


@router.post("/register")
def register(
    data: UsuarioCreate,
    service: UsuarioService = Depends(get_service),
    _admin=Depends(RoleChecker(ADMIN_ROLES)),
):
    return service.create_usuario(
        data,
        company_id=getattr(_admin, "id_company", None) or 1,
        motel_id=getattr(_admin, "id_motel", None) or 1,
    )


@router.post("/login")
def login(
    data: LoginRequest,
    request: Request,
    service: UsuarioService = Depends(get_service),
):
    key = _login_key(request, data.email)
    _assert_login_not_locked(key)
    try:
        response = service.login(data.email, data.password)
    except HTTPException as exc:
        if exc.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}:
            _record_failed_login(key)
        raise
    _clear_failed_login(key)
    return response
