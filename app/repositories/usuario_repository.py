from sqlalchemy.orm import Session
from app.models.usuario import Usuario

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Usuario).all()

    def get_by_id(self, usuario_id: int):
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_by_username(self, username: str):
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def create(self, usuario_data: dict):
        nuevo = Usuario(**usuario_data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def delete(self, usuario: Usuario):
        self.db.delete(usuario)
        self.db.commit()
