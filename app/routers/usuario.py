from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.repositories.usuario_repository import UsuarioRepository
from app.services.usuario_service import UsuarioService
from app.core.dependencies import obtener_usuario_actual
from app.models.usuario import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def get_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))

@router.get("/", response_model=list[UsuarioResponse])
def listar(service: UsuarioService = Depends(get_service), current_user: Usuario = Depends(obtener_usuario_actual)):
    return service.listar_usuarios()

@router.get("/me", response_model=UsuarioResponse)
def perfil(current_user: Usuario = Depends(obtener_usuario_actual)):
    return current_user

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener(usuario_id: int, service: UsuarioService = Depends(get_service), current_user: Usuario = Depends(obtener_usuario_actual)):
    return service.obtener_usuario(usuario_id)

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear(usuario: UsuarioCreate, service: UsuarioService = Depends(get_service)):
    return service.crear_usuario(usuario)

@router.delete("/{usuario_id}")
def eliminar(usuario_id: int, service: UsuarioService = Depends(get_service), current_user: Usuario = Depends(obtener_usuario_actual)):
    return service.eliminar_usuario(usuario_id)
