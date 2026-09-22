from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token
from app.repositories.usuario_repository import UsuarioRepository
from app.services.usuario_service import UsuarioService
from app.core.security import crear_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(datos: UsuarioCreate, service: UsuarioService = Depends(get_service)):
    existente = service.repository.get_by_username(datos.username)
    if existente:
        raise HTTPException(status_code=400, detail="El username ya existe")
    return service.crear_usuario(datos)

@router.post("/login", response_model=Token)
def login(datos: OAuth2PasswordRequestForm = Depends(), service: UsuarioService = Depends(get_service)):
    usuario = service.repository.get_by_username(datos.username)
    if not usuario or not service.verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    access_token = crear_token({"sub": usuario.username, "rol": usuario.rol})
    return Token(access_token=access_token)
