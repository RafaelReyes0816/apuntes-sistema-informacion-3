from fastapi import HTTPException
from app.repositories.producto_repository import ProductoRepository
from app.schemas.producto import ProductoCreate

class ProductoService:
    def __init__(self, repository: ProductoRepository):
        self.repository = repository

    def listar_productos(self):
        return self.repository.get_all()

    def obtener_producto(self, producto_id: int):
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto

    def crear_producto(self, datos: ProductoCreate):
        return self.repository.create(datos.model_dump())

    def eliminar_producto(self, producto_id: int):
        producto = self.obtener_producto(producto_id)
        self.repository.delete(producto)
        return {"mensaje": "Producto eliminado correctamente"}