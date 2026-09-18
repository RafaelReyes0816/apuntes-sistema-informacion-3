# FastAPI — proyecto pequeño en Ubuntu

Guía rápida para crear una API REST pequeña con FastAPI en Ubuntu.

> **Enfoque recomendado:** usar `uv` para gestionar Python, el entorno virtual y las dependencias. La documentación oficial actual de FastAPI recomienda `uv` y `fastapi[standard]` para empezar.  
> Fuentes: [FastAPI](https://fastapi.tiangolo.com/) · [uv](https://docs.astral.sh/uv/)

## 1. Video recomendado

**En español:**  
[⚡ Curso FastAPI con Python — DesarrolloLibre](https://www.youtube.com/watch?v=yQ35nqHaJ5c)

Es especialmente útil porque incluye preparación del entorno, instalación de paquetes, Hello World, Uvicorn, rutas y parámetros. El video también continúa con temas más avanzados.

Si quieres algo mucho más corto:

[✅ Crea tu Primera API con FastAPI en 10 Minutos — Cesar Sebastian Dev](https://www.youtube.com/watch?v=k0XG99NV1dY)

---

# 2. Preparar Ubuntu

Actualizar paquetes:

```bash
sudo apt update
sudo apt upgrade -y
```

Instalar herramientas básicas:

```bash
sudo apt install -y curl git
```

Comprobar Python:

```bash
python3 --version
```

FastAPI requiere Python 3.10 o superior para los ejemplos actuales de su documentación.

Si no tienes una versión adecuada, puedes dejar que `uv` gestione una versión de Python.

---

# 3. Instalar uv

`uv` es un gestor moderno de proyectos y paquetes Python. Permite crear el entorno virtual, instalar dependencias y mantener un archivo `uv.lock`.

Instalación oficial en Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Después, reinicia la terminal o carga nuevamente tu shell:

```bash
source ~/.bashrc
```

Comprobar:

```bash
uv --version
```

Si `uv` no aparece, abre una nueva terminal y vuelve a ejecutar:

```bash
uv --version
```

---

# 4. Crear el proyecto

Por ejemplo, vamos a crear una API llamada `fastapi-demo`:

```bash
uv init fastapi-demo --bare
cd fastapi-demo
```

La opción `--bare` crea una estructura mínima y deja que nosotros creemos `main.py`.

---

# 5. Instalar FastAPI y sus dependencias

Instalar FastAPI con las dependencias estándar:

```bash
uv add "fastapi[standard]"
```

Esto se encarga también de las dependencias necesarias para ejecutar FastAPI, incluyendo Uvicorn.

El proyecto tendrá:

```text
fastapi-demo/
├── .venv/
├── pyproject.toml
└── uv.lock
```

No necesitas ejecutar manualmente `pip install uvicorn` si instalaste:

```bash
uv add "fastapi[standard]"
```

---

# 6. Crear `main.py`

Crear el archivo:

```bash
touch main.py
```

Abrirlo con VS Code:

```bash
code main.py
```

Contenido:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hola desde FastAPI"}


@app.get("/saludo/{nombre}")
async def saludo(nombre: str):
    return {"message": f"Hola {nombre}"}
```

---

# 7. Ejecutar el servidor

Desde la carpeta del proyecto:

```bash
uv run fastapi dev
```

Deberías obtener una dirección similar a:

```text
http://127.0.0.1:8000
```

Abrir en el navegador:

```text
http://127.0.0.1:8000
```

También puedes probar:

```text
http://127.0.0.1:8000/saludo/Rafael
```

---

# 8. Swagger UI

Una de las ventajas de FastAPI es que genera documentación interactiva automáticamente.

Abre:

```text
http://127.0.0.1:8000/docs
```

También tienes ReDoc:

```text
http://127.0.0.1:8000/redoc
```

No necesitas instalar Swagger por separado.

---

# 9. Ejecutar con Uvicorn directamente

También puedes ejecutar la aplicación usando Uvicorn:

```bash
uv run uvicorn main:app --reload
```

Para permitir conexiones desde otros dispositivos de tu red:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

La expresión:

```text
main:app
```

significa:

- `main` → archivo `main.py`
- `app` → objeto `app = FastAPI()`

---

# 10. Agregar una ruta POST

Ejemplo sencillo usando Pydantic:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Usuario(BaseModel):
    nombre: str
    edad: int


@app.get("/")
async def root():
    return {"message": "API funcionando"}


@app.post("/usuarios")
async def crear_usuario(usuario: Usuario):
    return {
        "message": "Usuario creado",
        "usuario": usuario
    }
```

FastAPI validará automáticamente:

```json
{
  "nombre": "Rafael",
  "edad": 25
}
```

Puedes probar el POST directamente desde:

```text
http://127.0.0.1:8000/docs
```

---

# 11. Comandos importantes

## Crear proyecto

```bash
uv init fastapi-demo --bare
cd fastapi-demo
```

## Instalar FastAPI

```bash
uv add "fastapi[standard]"
```

## Ejecutar en desarrollo

```bash
uv run fastapi dev
```

## Ejecutar con Uvicorn

```bash
uv run uvicorn main:app --reload
```

## Ejecutar escuchando en toda la red

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## Sincronizar dependencias

```bash
uv sync
```

## Ver dependencias

```bash
uv tree
```

## Actualizar el lockfile

```bash
uv lock
```

---

# 12. Estructura recomendada cuando el proyecto crezca

Para una API pequeña puedes comenzar con:

```text
fastapi-demo/
├── .venv/
├── main.py
├── pyproject.toml
└── uv.lock
```

Cuando empiece a crecer, conviene separar responsabilidades:

```text
fastapi-demo/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── usuarios.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── database/
├── .venv/
├── pyproject.toml
└── uv.lock
```

No hace falta montar esa arquitectura para un CRUD de tres endpoints. Empezar pequeño evita convertir un "Hola Mundo" en Kubernetes antes del desayuno.

---

# 13. Git

Inicializar repositorio:

```bash
git init
```

Crear `.gitignore`:

```bash
touch .gitignore
```

Agregar:

```gitignore
.venv/
__pycache__/
*.pyc
.env
```

Luego:

```bash
git add .
git commit -m "Initial FastAPI project"
```

**Importante:** no subas `.venv/`. El archivo `uv.lock` sí debe versionarse porque permite reproducir las versiones de las dependencias.

---

# 14. Dependencias que realmente necesitas

Para comenzar:

```text
fastapi[standard]
```

No necesitas instalar individualmente:

```text
uvicorn
starlette
pydantic
```

cuando utilizas `fastapi[standard]`, porque las dependencias estándar ya incluyen lo necesario para este flujo.

Si posteriormente necesitas una base de datos, autenticación, configuración mediante variables de entorno, etc., puedes agregar solamente lo que el proyecto necesite.

Ejemplo:

```bash
uv add sqlalchemy
```

o:

```bash
uv add psycopg[binary]
```

para PostgreSQL.

---

# 15. Flujo completo desde cero

Si quieres copiar y pegar prácticamente todo:

```bash
sudo apt update
sudo apt install -y curl git

curl -LsSf https://astral.sh/uv/install.sh | sh

source ~/.bashrc

uv --version

uv init fastapi-demo --bare
cd fastapi-demo

uv add "fastapi[standard]"

touch main.py
code main.py

uv run fastapi dev
```

Después abre:

```text
http://127.0.0.1:8000/docs
```

---

## Referencias oficiales

- [FastAPI — documentación oficial](https://fastapi.tiangolo.com/)
- [FastAPI — primeros pasos](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI — tutorial](https://fastapi.tiangolo.com/tutorial/)
- [uv — instalación](https://docs.astral.sh/uv/getting-started/installation/)
- [uv — integración con FastAPI](https://docs.astral.sh/uv/guides/integration/fastapi/)
