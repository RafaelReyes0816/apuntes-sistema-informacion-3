# FastAPI + PostgreSQL + Clean Architecture

Guía paso a paso para crear un proyecto FastAPI con PostgreSQL, SQLAlchemy y arquitectura limpia usando `uv`.

---

## 1. Crear el proyecto

```bash
uv init mi-api --bare
cd mi-api
```

---

## 2. Instalar dependencias

```bash
uv add "fastapi[standard]"
uv add sqlalchemy
uv add psycopg2-binary
uv add python-dotenv
```

Esto instala:
- **FastAPI** con dependencias estándar (uvicorn, pydantic, etc.)
- **SQLAlchemy** ORM para modelos y sesiones
- **psycopg2** driver de PostgreSQL
- **python-dotenv** para leer variables de entorno desde `.env`

---

## 3. Crear archivo `.env`

```bash
touch .env
```

Contenido:

```
DATABASE_URL=postgresql+psycopg2://usuario:contraseña@localhost:puerto/nombre_bd
```

Ejemplo:

```
DATABASE_URL=postgresql+psycopg2://postgres:123456@localhost:5432/mi_basededatos
```

**Importante:** nunca subas `.env` a git.

---

## 4. Crear `.gitignore`

```bash
touch .gitignore
```

Contenido:

```
.venv/
__pycache__/
*.pyc
.env
*.db
```

---

## 5. Crear la estructura de carpetas

```bash
mkdir -p app/models app/schema app/routes
touch app/__init__.py
touch app/models/__init__.py
touch app/schema/__init__.py
touch app/routes/__init__.py
```

Estructura resultante:

```text
mi-api/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── producto.py
│   ├── schema/
│   │   ├── __init__.py
│   │   └── producto.py
│   └── routes/
│       ├── __init__.py
│       └── producto.py
├── .env
├── .gitignore
├── main.py
├── pyproject.toml
└── uv.lock
```

---

## 6. Crear `app/database.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

---

## 7. Crear el modelo `app/models/producto.py`

```python
from sqlalchemy import Column, Float, Integer, String
from app.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float)
    stock = Column(Integer, default=0)
```

---

## 8. Crear el schema `app/schema/producto.py`

```python
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
```

---

## 9. Crear la ruta `app/routes/producto.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.producto import Producto as ProductoModel
from app.schema.producto import Producto, ProductoCreate

router = APIRouter(prefix="/productos", tags=["Productos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[Producto])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(ProductoModel).all()


@router.get("/{producto_id}", response_model=Producto)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(ProductoModel, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/", response_model=Producto, status_code=201)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    db_producto = ProductoModel(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.put("/{producto_id}", response_model=Producto)
def actualizar_producto(
    producto_id: int, producto: ProductoCreate, db: Session = Depends(get_db)
):
    db_producto = db.get(ProductoModel, producto_id)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in producto.model_dump().items():
        setattr(db_producto, campo, valor)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.get(ProductoModel, producto_id)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_producto)
    db.commit()
```

---

## 10. Crear `main.py`

```python
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import producto

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Productos", description="API para gestionar productos")
app.include_router(producto.router)
```

`Base.metadata.create_all` crea las tablas automáticamente en PostgreSQL al iniciar la app.

---

## 11. Ejecutar el servidor

```bash
uv run uvicorn main:app --reload
```

Verificar:

- API: `http://127.0.0.1:8000/productos/`
- Documentación: `http://127.0.0.1:8000/docs`

---

## 12. Crear la base de datos en PostgreSQL (pgAdmin)

Si aún no tienes la base de datos, desde pgAdmin o la consola de PostgreSQL:

```sql
CREATE DATABASE mi_basededatos;
```

O desde la terminal:

```bash
createdb -U localhost -p 5432 mi_basededatos
```

---

## 13. Estructura de archivos explicada

| Archivo | Función |
|---------|---------|
| `app/database.py` | Conexión a la BD, engine, session, Base |
| `app/models/` | Modelos SQLAlchemy (tablas) |
| `app/schema/` | Schemas Pydantic (validación de entrada/salida) |
| `app/routes/` | Endpoints (rutas de la API) |
| `main.py` | Punto de entrada, crea las tablas y monta routers |
| `.env` | Variables de entorno (DATABASE_URL) |

---

## 14. Agregar un nuevo recurso (ej: categorías)

1. Crear `app/models/categoria.py` con el modelo
2. Crear `app/schema/categoria.py` con los schemas
3. Crear `app/routes/categoria.py` con los endpoints
4. Importar el router en `main.py` y agregar `app.include_router(categoria.router)`
5. Importar el modelo en `main.py` para que `create_all` lo detecte

---

## 15. Errores comunes

### `ModuleNotFoundError: No module named 'app'`

La carpeta `app/` no existe o no tiene `__init__.py`. Solución:

```bash
mkdir -p app
touch app/__init__.py
```

### `password authentication failed`

La contraseña en `.env` no coincide con la de PostgreSQL. Verifica el archivo `.env`.

### `relation "productos" does not exist`

Las tablas no se crearon. Ejecuta la app una vez (`Base.metadata.create_all` las crea automáticamente).

---

## Referencias

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [uv](https://docs.astral.sh/uv/)
- [psycopg2](https://www.psycopg.org/docs/)
