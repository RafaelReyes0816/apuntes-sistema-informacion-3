from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.usuario_repository import UsuarioRepository
from app.services.usuario_service import UsuarioService
from app.core.dependencies import obtener_usuario_actual
