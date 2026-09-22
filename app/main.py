from fastapi import FastAPI
from app.database import Base, engine
from app.routers import producto, usuario, auth
from app.core.middlewares import configurar_middlewares

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Informacion - Proyecto Integrador")
configurar_middlewares(app)
app.include_router(producto.router)
app.include_router(usuario.router)
app.include_router(auth.router)