from fastapi import FastAPI
from app.database import Base, engine
from app.routers import producto

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Informacion - Proyecto Integrador")
app.include_router(producto.router)