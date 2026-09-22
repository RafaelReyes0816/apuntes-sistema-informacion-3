from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decodificar_token
from app.repositories.usuario_repository import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decodificar_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")

    username = payload.get("sub")
    usuario = UsuarioRepository(db).get_by_username(username)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return usuario


def requerir_rol(rol_requerido: str):
    """Dependencia adicional: exige que el usuario autenticado tenga un rol especifico."""
    def verificar(usuario=Depends(obtener_usuario_actual)):
        if usuario.rol != rol_requerido:
            raise HTTPException(status_code=403, detail="No tiene permisos para esta accion")
        return usuario
    return verificar
