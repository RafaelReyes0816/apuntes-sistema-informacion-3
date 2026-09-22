from fastapi import HTTPException
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate
from app.core.security import hashear_password, verificar_password

class UsuarioService:
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def listar_usuarios(self):
        return self.repository.get_all()

    def obtener_usuario(self, usuario_id: int):
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario

    def crear_usuario(self, datos: UsuarioCreate):
        existente = self.repository.get_by_username(datos.username)
        if existente:
            raise HTTPException(status_code=400, detail="El username ya existe")
        usuario_data = datos.model_dump()
        usuario_data["password_hash"] = hashear_password(usuario_data.pop("password"))
        return self.repository.create(usuario_data)

    def eliminar_usuario(self, usuario_id: int):
        usuario = self.obtener_usuario(usuario_id)
        self.repository.delete(usuario)
        return {"mensaje": "Usuario eliminado correctamente"}

    def verificar_password(self, password: str, password_hash: str):
        return verificar_password(password, password_hash)
