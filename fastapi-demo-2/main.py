from fastapi import FastAPI
from app.database import Base, engine
from app.routes import producto

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Productos", description="API para gestionar productos")
app.include_router(producto.router)