from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.producto import ProductoCreate, ProductoResponse
from app.repositories.producto_repository import ProductoRepository
from app.services.producto_service import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])

def get_service(db: Session = Depends(get_db)) -> ProductoService:
    return ProductoService(ProductoRepository(db))

@router.get("/", response_model=list[ProductoResponse])
def listar(service: ProductoService = Depends(get_service)):
    return service.listar_productos()

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener(producto_id: int, service: ProductoService = Depends(get_service)):
    return service.obtener_producto(producto_id)

@router.post("/", response_model=ProductoResponse, status_code=201)
def crear(producto: ProductoCreate, service: ProductoService = Depends(get_service)):
    return service.crear_producto(producto)

@router.delete("/{producto_id}")
def eliminar(producto_id: int, service: ProductoService = Depends(get_service)):
    return service.eliminar_producto(producto_id)