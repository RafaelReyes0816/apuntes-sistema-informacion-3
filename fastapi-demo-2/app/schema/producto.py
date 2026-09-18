from pydantic import BaseModel


class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock: int = 0


class ProductoCreate(ProductoBase):
    pass


class Producto(ProductoBase):
    id: int

    model_config = {"from_attributes": True}