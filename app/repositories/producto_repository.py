from sqlalchemy.orm import Session
from app.models.producto import Producto

class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Producto).all()

    def get_by_id(self, producto_id: int):
        return self.db.query(Producto).filter(Producto.id == producto_id).first()

    def create(self, producto_data: dict):
        nuevo = Producto(**producto_data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def delete(self, producto: Producto):
        self.db.delete(producto)
        self.db.commit()