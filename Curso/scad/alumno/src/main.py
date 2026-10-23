"""
Aplicación FastAPI de SCAD (versión alumno).

Ejercicios resueltos del curso:
- Día 1: Rutas básicas y /validar-destino
- Día 2: Modelos SQLModel + SQLite
- Día 3: Autenticación HTTP Basic + CRUD protegido
- Día 3 Bloque 2: Middleware de logging y auditoría
- Día 4: Frontend con Jinja2, HTMX y Markdown
"""

import secrets
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional

import markdown
from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from alumno.src.logger import logger
from alumno.src.models import (
    Aviso,
    AvisoCreate,
    AvisoUpdate,
    crear_db_y_tablas,
    get_session,
)

# ---------------------------------------------------------------------------
# Configuración de rutas
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


# ---------------------------------------------------------------------------
# Lifespan: creación de tablas al arrancar
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_db_y_tablas()
    yield


# ---------------------------------------------------------------------------
# Instancia de la aplicación
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SCAD - Sistema Centralizado de Avisos",
    description="Ejercicio práctico del curso Python + FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware de auditoría y logging
# ---------------------------------------------------------------------------

@app.middleware("http")
async def registrar_auditoria_middleware(request: Request, call_next):
    tiempo_inicio = time.perf_counter()
    ip_cliente = request.client.host if request.client else "Desconocida"
    metodo = request.method
    url = request.url.path

    try:
        response = await call_next(request)
        tiempo_proceso_ms = (time.perf_counter() - tiempo_inicio) * 1000
        codigo_estado = response.status_code

        mensaje_log = (
            f"IP: {ip_cliente} | {metodo} {url} | "
            f"Estado: {codigo_estado} | Tiempo: {tiempo_proceso_ms:.2f}ms"
        )

        if codigo_estado < 400:
            logger.info(mensaje_log)
        elif 400 <= codigo_estado < 500:
            logger.warning(mensaje_log)
        else:
            logger.error(mensaje_log)

        response.headers["X-Process-Time-MS"] = f"{tiempo_proceso_ms:.2f}"
        return response

    except Exception as exc:
        tiempo_proceso_ms = (time.perf_counter() - tiempo_inicio) * 1000
        logger.error(
            f"IP: {ip_cliente} | {metodo} {url} | "
            f"EXCEPCIÓN NO CONTROLADA: {str(exc)} | "
            f"Tiempo: {tiempo_proceso_ms:.2f}ms"
        )
        raise exc


# ---------------------------------------------------------------------------
# Archivos estáticos y plantillas Jinja2
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def filtro_markdown(texto: str) -> str:
    """Filtro personalizado de Markdown para Jinja2."""
    if not texto:
        return ""
    return markdown.markdown(
        texto,
        extensions=["fenced_code", "tables", "nl2br"],
    )


templates.env.filters["markdown"] = filtro_markdown


# ---------------------------------------------------------------------------
# Autenticación HTTP Basic (inline por simplicidad)
# ---------------------------------------------------------------------------

security = HTTPBasic()

ADMIN_USERS = {
    "admin_dom": "P@ssw0rd2026",
    "soporte_dom": "AdminSCAD123",
}


def obtener_usuario_admin_actual(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    """Dependencia de seguridad que valida la autenticación HTTP Basic."""
    usuario_correcto = False
    if credentials.username in ADMIN_USERS:
        password_almacenada = ADMIN_USERS[credentials.username]
        usuario_correcto = secrets.compare_digest(
            credentials.password.encode("utf-8"),
            password_almacenada.encode("utf-8"),
        )

    if not usuario_correcto:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administración incorrectas o no proporcionadas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ---------------------------------------------------------------------------
# Esquema para el ejercicio de validación de destino
# ---------------------------------------------------------------------------

class TipoDestinoValidar(str, Enum):
    USUARIO = "usuario"
    EQUIPO = "equipo"
    GRUPO = "grupo"
    OU = "ou"


class SolicitudValidacionDestino(BaseModel):
    tipo_destino: TipoDestinoValidar
    nombre_destino: str = Field(min_length=3, max_length=50)


# ===========================================================================
# RUTAS BÁSICAS (Día 1)
# ===========================================================================

@app.get("/", response_class=HTMLResponse)
def mostrar_tablon_avisos(
    request: Request,
    destino: Optional[str] = None,
    session: Session = Depends(get_session),
    hx_request: Optional[str] = Header(None, alias="HX-Request"),
):
    """Tablón de avisos con Jinja2 + HTMX."""
    query = select(Aviso).where(Aviso.activo == True)  # noqa: E712

    if destino and destino.strip() != "":
        query = query.where(Aviso.destino == destino)

    avisos = session.exec(query).all()

    context = {
        "avisos": avisos,
        "destino_actual": destino,
    }

    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="_lista_avisos.html",
            context=context,
        )

    return templates.TemplateResponse(
        request=request,
        name="avisos.html",
        context=context,
    )


@app.get("/version")
def obtener_version():
    return {
        "app": "SCAD",
        "version": "1.0.0",
        "organizacion": "MiDominio",
    }


@app.get("/equipo-desarrollo")
def obtener_equipo():
    return {
        "equipo": ["Admin General", "Soporte Técnico", "Operaciones IT"],
        "total_miembros": 3,
    }


@app.get("/info-dominio")
def obtener_info_dominio():
    return {
        "nombre_dominio": "empresa.local",
        "servidor_dc": "DC01.empresa.local",
        "estado_dc": "activo",
    }


# ===========================================================================
# VALIDACIÓN DE DESTINO (Día 1 - Bloque 2)
# ===========================================================================

@app.post("/validar-destino")
def validar_destino(datos: SolicitudValidacionDestino):
    nombre = datos.nombre_destino.strip()

    # Validación adicional de negocio para equipos del dominio
    if datos.tipo_destino == TipoDestinoValidar.EQUIPO:
        if not (nombre.startswith("PC-") or nombre.startswith("SRV-")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los nombres de equipo deben empezar por PC- o SRV-",
            )

    return {
        "valido": True,
        "destino": f"{datos.tipo_destino.value}:{nombre}",
    }


# ===========================================================================
# CRUD DE AVISOS (Día 2 + Día 3 con auth)
# ===========================================================================

# 1. CREAR AVISO (POST) - protegido
@app.post("/avisos", response_model=Aviso, status_code=status.HTTP_201_CREATED)
def crear_aviso_protegido(
    aviso_in: AvisoCreate,
    usuario_admin: str = Depends(obtener_usuario_admin_actual),
    session: Session = Depends(get_session),
):
    nuevo_aviso = Aviso.model_validate(
        aviso_in,
        update={"creado_por": usuario_admin},
    )
    session.add(nuevo_aviso)
    session.commit()
    session.refresh(nuevo_aviso)
    return nuevo_aviso


# 2. LISTAR AVISOS CON FILTROS (GET) - público
@app.get("/avisos", response_model=List[Aviso])
def listar_avisos(
    destino: Optional[str] = None,
    solo_activos: bool = True,
    session: Session = Depends(get_session),
):
    query = select(Aviso)
    if solo_activos:
        query = query.where(Aviso.activo == True)  # noqa: E712
    if destino:
        query = query.where(Aviso.destino == destino)
    avisos = session.exec(query).all()
    return avisos


# 3. OBTENER UN AVISO POR ID (GET) - público
@app.get("/avisos/{aviso_id}", response_model=Aviso)
def obtener_aviso(aviso_id: int, session: Session = Depends(get_session)):
    aviso = session.get(Aviso, aviso_id)
    if not aviso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se ha encontrado el aviso con ID {aviso_id}",
        )
    return aviso


# 4. ACTUALIZAR PARCIALMENTE UN AVISO (PATCH) - protegido
@app.patch("/avisos/{aviso_id}", response_model=Aviso)
def actualizar_aviso_protegido(
    aviso_id: int,
    aviso_update: AvisoUpdate,
    usuario_admin: str = Depends(obtener_usuario_admin_actual),
    session: Session = Depends(get_session),
):
    aviso_db = session.get(Aviso, aviso_id)
    if not aviso_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se ha encontrado el aviso con ID {aviso_id}",
        )

    datos = aviso_update.model_dump(exclude_unset=True)
    for clave, valor in datos.items():
        setattr(aviso_db, clave, valor)

    aviso_db.modificado_por = usuario_admin
    aviso_db.modificado_en = datetime.now(timezone.utc)

    session.add(aviso_db)
    session.commit()
    session.refresh(aviso_db)
    return aviso_db


# 5. ELIMINAR UN AVISO (DELETE) - protegido
@app.delete("/avisos/{aviso_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_aviso(
    aviso_id: int,
    usuario_admin: str = Depends(obtener_usuario_admin_actual),
    session: Session = Depends(get_session),
):
    aviso_db = session.get(Aviso, aviso_id)
    if not aviso_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se ha encontrado el aviso con ID {aviso_id}",
        )
    session.delete(aviso_db)
    session.commit()
    return None
