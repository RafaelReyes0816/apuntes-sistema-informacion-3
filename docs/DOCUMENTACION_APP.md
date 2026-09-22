# Documentacion del Proyecto FastAPI - Estructura con Arquitectura por Capas

## Indice

1. [Estructura del proyecto](#1-estructura-del-proyecto)
2. [Flujo de datos (request/response)](#2-flujo-de-datos)
3. [Conexion a base de datos](#3-conexion-a-base-de-datos)
4. [Descripcion de cada capa](#4-descripcion-de-cada-capa)
5. [Crear un modulo nuevo (paso a paso)](#5-crear-un-modulo-nuevo)
6. [Comandos utiles](#6-comandos-utiles)
7. [Errores comunes y soluciones](#7-errores-comunes-y-soluciones)

---

## 1. Estructura del proyecto

```
clase/
├── .env                          # Variables de entorno (DATABASE_URL)
├── requirements.txt              # Dependencias del proyecto
├── venv/                         # Entorno virtual (no se sube a git)
└── app/
    ├── __init__.py               # convierte app/ en paquete Python
    ├── main.py                   # Punto de entrada - crea la app FastAPI
    ├── database.py               # Configuracion de SQLAlchemy y conexion a BD
    ├── models/
    │   ├── __init__.py
    │   └── producto.py           # Modelo SQLAlchemy (tabla productos)
    ├── schemas/
    │   ├── __init__.py
    │   └── producto.py           # Schemas Pydantic (validacion de datos)
    ├── repositories/
    │   ├── __init__.py
    │   └── producto_repository.py  # Acceso a la base de datos (CRUD)
    ├── services/
    │   ├── __init__.py
    │   └── producto_service.py   # Logica de negocio
    └── routers/
        ├── __init__.py
        └── producto.py           # Endpoints HTTP (rutas de la API)
```

**Regla de oro:** Todos los imports dentro de `app/` usan el prefijo `app.`:

```python
# CORRECTO
from app.database import Base
from app.models.producto import Producto

# INCORRECTO
from database import Base
from models.producto import Producto
```

---

## 2. Flujo de datos

Un request HTTP recorre el proyecto en este orden:

```
Cliente (navegador/Postman/curl)
    │
    ▼
┌─────────────┐
│  RUTAS      │  router/producto.py  ← recibe el request HTTP
│  (endpoints)│  valida con schemas Pydantic
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  SERVICES   │  services/producto_service.py  ← logica de negocio
│             │  validaciones, reglas, transformaciones
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ REPOSITORY  │  repositories/producto_repository.py  ← acceso a BD
│             │  queries SQL via SQLAlchemy
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MODELS     │  models/producto.py  ← define la tabla en la BD
│             │  Column, Integer, String, etc.
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  DATABASE   │  database.py  ← engine, sesion, conexion
└─────────────┘
```

**Ejemplo concreto - POST /productos/:**

1. **Ruta** recibe JSON `{"nombre": "Laptop", "precio": 999.99, "stock": 5}`
2. **Schema** `ProductoCreate` valida: nombre tiene 2-100 chars, precio > 0, stock >= 0
3. **Service** recibe el schema validado y lo pasa al repository
4. **Repository** crea el objeto `Producto` y hace `db.add()` + `db.commit()`
5. **Modelo** inserta el registro en la tabla `productos`
6. **Ruta** retorna el objeto creado con su `id` (status 201)

---

## 3. Conexion a base de datos

### Archivo `.env`

```env
DATABASE_URL=postgresql://postgres:160801@localhost:5433/productos
```

Formato: `postgresql://USUARIO:CONTRASENA@HOST:PUERTO/NOMBRE_BD`

### Archivo `database.py` - que hace cada parte

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# 1. Carga las variables del .env
load_dotenv()

# 2. Lee la URL de conexion
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Crea el engine (maneja la conexion pooling)
engine = create_engine(DATABASE_URL)

# 4. Crea la fabrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base para los modelos (todos heredan de aqui)
Base = declarative_base()

# 6. Generador de sesiones para inyectar en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Como funciona `get_db()`

```python
# FastAPI inyecta la sesion automaticamente con Depends()
@router.get("/")
def listar(db: Session = Depends(get_db)):
    # db ya es una sesion abierta y lista para usar
    return db.query(Producto).all()
    # despues del return, se ejecuta db.close() automaticamente
```

### Cambiar a SQLite (sin PostgreSQL)

En `.env` cambiar a:
```env
DATABASE_URL=sqlite:///./productos.db
```

En `database.py` agregar `connect_args`:
```python
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

---

## 4. Descripcion de cada capa

### 4.1 `app/main.py` - Punto de entrada

```python
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import producto

# Crea las tablas en la BD si no existen
Base.metadata.create_all(bind=engine)

# Crea la aplicacion FastAPI
app = FastAPI(title="Sistema de Informacion - Proyecto Integrador")

# Registra el router (agrega los endpoints de producto)
app.include_router(producto.router)
```

**Que hace:** Crea la app, crea las tablas, registra las rutas. Es lo que ejecuta uvicorn.

### 4.2 `app/models/` - Modelos SQLAlchemy

```python
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Producto(Base):
    __tablename__ = "productos"          # nombre de la tabla en la BD

    id = Column(Integer, primary_key=True, index=True)  # PK autoincremental
    nombre = Column(String(100), nullable=False)         # string max 100, obligatorio
    precio = Column(Float, nullable=False)               # decimal, obligatorio
    stock = Column(Integer, default=0)                   # entero, default 0
```

**Tipos de columna disponibles:**

| Tipo | Python | SQL |
|------|--------|-----|
| `Integer` | `int` | `INT` |
| `String(n)` | `str` | `VARCHAR(n)` |
| `Text` | `str` | `TEXT` |
| `Float` | `float` | `FLOAT` |
| `Boolean` | `bool` | `BOOLEAN` |
| `DateTime` | `datetime` | `TIMESTAMP` |
| `Date` | `date` | `DATE` |

### 4.3 `app/schemas/` - Schemas Pydantic

```python
from pydantic import BaseModel, Field

# Schema base - campos compartidos
class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)  # obligatorio, 2-100 chars
    precio: float = Field(..., gt=0)                         # obligatorio, > 0
    stock: int = Field(default=0, ge=0)                      # opcional, default 0, >= 0

# Schema para CREAR - hereda de base, sin cambios
class ProductoCreate(ProductoBase):
    pass

# Schema para RESPUESTA - agrega el id
class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True  # permite convertir desde objetos SQLAlchemy
```

**Validaciones de Field:**

| Parametro | Significado | Ejemplo |
|-----------|-------------|---------|
| `...` | obligatorio | `Field(...)` |
| `default=val` | valor por defecto | `Field(default=0)` |
| `gt=0` | mayor que | `Field(gt=0)` |
| `ge=0` | mayor o igual que | `Field(ge=0)` |
| `lt=100` | menor que | `Field(lt=100)` |
| `min_length=2` | longitud minima | `Field(min_length=2)` |
| `max_length=100` | longitud maxima | `Field(max_length=100)` |

### 4.4 `app/repositories/` - Acceso a BD

```python
from sqlalchemy.orm import Session
from app.models.producto import Producto

class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db                    # recibe la sesion de SQLAlchemy

    def get_all(self):
        return self.db.query(Producto).all()           # SELECT * FROM productos

    def get_by_id(self, producto_id: int):
        return self.db.query(Producto).filter(Producto.id == producto_id).first()
        # SELECT * FROM productos WHERE id = ?

    def create(self, producto_data: dict):
        nuevo = Producto(**producto_data)   # crea el objeto modelo
        self.db.add(nuevo)                  # INSERT
        self.db.commit()                    # confirma la transaccion
        self.db.refresh(nuevo)              # recarga con el id generado
        return nuevo

    def delete(self, producto: Producto):
        self.db.delete(producto)            # DELETE
        self.db.commit()
```

**Metodos de query mas comunes:**

```python
# Filtrar
db.query(Producto).filter(Producto.nombre == "Laptop").first()

# Filtrar con multiples condiciones
db.query(Producto).filter(Producto.precio < 1000, Producto.stock > 0).all()

# Ordenar
db.query(Producto).order_by(Producto.precio.desc()).all()

# Limitar
db.query(Producto).limit(10).all()

# Contar
db.query(Producto).count()
```

### 4.5 `app/services/` - Logica de negocio

```python
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
```

**Para que sirve la capa de services:**
- Validar reglas de negocio que no van en el schema
- Lanzar HTTPException con mensajes claros
- Combinar llamadas a multiples repositories
- Transformar datos antes de guardar o despues de leer

### 4.6 `app/routers/` - Endpoints HTTP

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.producto import ProductoCreate, ProductoResponse
from app.repositories.producto_repository import ProductoRepository
from app.services.producto_service import ProductoService

# Prefix = ruta base, Tags = agrupa en Swagger UI
router = APIRouter(prefix="/productos", tags=["Productos"])

# Dependency injection: crea el service con su repository
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
```

**Endpoints disponibles:**

| Metodo | Ruta | Descripcion | Body |
|--------|------|-------------|------|
| `GET` | `/productos/` | Listar todos | - |
| `GET` | `/productos/{id}` | Obtener uno por ID | - |
| `POST` | `/productos/` | Crear uno nuevo | `ProductoCreate` |
| `DELETE` | `/productos/{id}` | Eliminar uno | - |

---

## 5. Crear un modulo nuevo (paso a paso)

Ejemplo: crear un modulo `usuario` con campos `nombre`, `email`, `rol`.

### Paso 1: Crear el modelo (`app/models/usuario.py`)

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    rol = Column(String(50), default="user")
```

### Paso 2: Crear el schema (`app/schemas/usuario.py`)

```python
from pydantic import BaseModel, Field, EmailStr

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=150)
    rol: str = Field(default="user", max_length=50)

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True
```

### Paso 3: Crear el repository (`app/repositories/usuario_repository.py`)

```python
from sqlalchemy.orm import Session
from app.models.usuario import Usuario

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Usuario).all()

    def get_by_id(self, usuario_id: int):
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_by_email(self, email: str):
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def create(self, usuario_data: dict):
        nuevo = Usuario(**usuario_data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def delete(self, usuario: Usuario):
        self.db.delete(usuario)
        self.db.commit()
```

### Paso 4: Crear el service (`app/services/usuario_service.py`)

```python
from fastapi import HTTPException
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate

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
        existente = self.repository.get_by_email(datos.email)
        if existente:
            raise HTTPException(status_code=400, detail="El email ya esta registrado")
        return self.repository.create(datos.model_dump())

    def eliminar_usuario(self, usuario_id: int):
        usuario = self.obtener_usuario(usuario_id)
        self.repository.delete(usuario)
        return {"mensaje": "Usuario eliminado correctamente"}
```

### Paso 5: Crear el router (`app/routers/usuario.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.repositories.usuario_repository import UsuarioRepository
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def get_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))

@router.get("/", response_model=list[UsuarioResponse])
def listar(service: UsuarioService = Depends(get_service)):
    return service.listar_usuarios()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener(usuario_id: int, service: UsuarioService = Depends(get_service)):
    return service.obtener_usuario(usuario_id)

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear(usuario: UsuarioCreate, service: UsuarioService = Depends(get_service)):
    return service.crear_usuario(usuario)

@router.delete("/{usuario_id}")
def eliminar(usuario_id: int, service: UsuarioService = Depends(get_service)):
    return service.eliminar_usuario(usuario_id)
```

### Paso 6: Registrar el router en `app/main.py`

```python
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import producto, usuario  # <-- agregar usuario

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Informacion - Proyecto Integrador")
app.include_router(producto.router)
app.include_router(usuario.router)  # <-- agregar esta linea
```

---

## 6. Comandos utiles

### Ejecutar el proyecto

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar con recarga automatica
uvicorn app.main:app --reload

# Ejecutar en red local (accesible desde otros dispositivos)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### URLs de prueba

```
http://127.0.0.1:8000/docs        # Swagger UI (interfaz para probar)
http://127.0.0.1:8000/redoc       # ReDoc (documentacion alternativa)
http://127.0.0.1:8000/productos/  # GET listar productos
```

### Dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt

# Guardar dependencias actuales
pip freeze > requirements.txt

# Salir del entorno virtual
deactivate
```

### Base de datos

```bash
# Conectar a la BD desde terminal
psql -h localhost -p 5433 -U postgres -d productos

# Listar tablas
\dt

# Ver estructura de una tabla
\d productos

# Salir de psql
\q
```

---

## 7. Errores comunes y soluciones

### `ModuleNotFoundError: No module named 'app'`

**Causa:** Estas ejecutando uvicorn desde la carpeta equivocada.

**Solucion:** Ejecuta desde `clase/`, no desde `clase/app/`:
```bash
# CORRECTO (desde clase/)
uvicorn app.main:app --reload

# INCORRECTO (desde clase/app/)
uvicorn main:app --reload
```

### `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection refused`

**Causa:** PostgreSQL no esta corriendo o los datos de conexion son incorrectos.

**Solucion:**
1. Verificar que PostgreSQL este activo: `pg_isready -h localhost -p 5433`
2. Verificar el `.env` tenga los datos correctos
3. Verificar que la BD exista

### `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: database "productos" does not exist`

**Solucion:** Crear la BD:
```bash
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE productos;"
```

### `pydantic.ValidationError: Field required`

**Causa:** El JSON enviado no tiene todos los campos obligatorios.

**Solucion:** Verificar en el schema que campos son obligatorios (usan `...`).

### `422 Unprocessable Entity`

**Causa:** El request es correcto pero los datos no pasan la validacion.

**Solucion:** Revisar los constraints del schema (min_length, gt, ge, etc.).

---

## Plantilla para copiar y pegar

Cuando crees un proyecto nuevo, copia esta estructura:

```bash
# Crear proyecto
mkdir mi-proyecto && cd mi-proyecto

# Entorno virtual
python -m venv venv
source venv/bin/activate

# Estructura
mkdir app app/models app/schemas app/repositories app/services app/routers
touch app/__init__.py app/main.py app/database.py .env
touch app/models/__init__.py app/schemas/__init__.py
touch app/repositories/__init__.py app/services/__init__.py
touch app/routers/__init__.py

# Dependencias
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv psycopg2-binary
pip freeze > requirements.txt

# Ejecutar
uvicorn app.main:app --reload
```
