"""
Aplicación FastAPI principal de SCAD (versión profesor).

Combina todas las funcionalidades del curso:
- Persistencia con SQLModel + SQLite
- Autenticación HTTP Basic para rutas de administración
- Middleware de auditoría y logging en fichero
- Frontend con Jinja2, HTMX y conversión Markdown → HTML
- CRUD completo de avisos
- Endpoint de evaluación para el script de logon
- Portal web de avisos para el navegador
"""

import base64
import json
import sys
import time
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import markdown
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from profesor.src.auth import obtener_usuario_admin_actual
from profesor.src.evaluador import obtener_avisos_vigentes_para_cliente
from profesor.src.logger import logger
from profesor.src.models import (
    Aviso,
    AvisoCreate,
    AvisoUpdate,
    crear_db_y_tablas,
    get_session,
)
from profesor.src.schemas import PeticionDeLogon, RespuestaParaLogon

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
    title="SCAD - Sistema Centralizado de Avisos de Dominio",
    description="API para la gestión y distribución de avisos a equipos y usuarios de dominio",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Manejador de excepciones global (debug)
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    sys.stderr.write("\n" + "=" * 80 + "\n")
    sys.stderr.write(f" EXCEPCIÓN EN PETICIÓN: {request.method} {request.url.path}\n")
    sys.stderr.write("=" * 80 + "\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write("=" * 80 + "\n\n")
    sys.stderr.flush()
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "type": type(exc).__name__,
            "message": "Revisa la terminal para ver el traceback completo.",
            "path": request.url.path,
        },
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


# Filtro personalizado de Markdown para Jinja2
def filtro_markdown(texto: str) -> str:
    if not texto:
        return ""
    return markdown.markdown(
        texto,
        extensions=["fenced_code", "tables", "nl2br"],
    )


templates.env.filters["markdown"] = filtro_markdown


def md_to_html(text: str) -> str:
    """Convierte texto Markdown a HTML."""
    if not text:
        return ""
    return markdown.markdown(text, extensions=["fenced_code", "tables", "nl2br"])


# ---------------------------------------------------------------------------
# RUTAS CRUD DE AVISOS
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# RUTA WEB: Tablón de avisos con HTMX (GET /)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def mostrar_tablon_avisos(
    request: Request,
    destino: Optional[str] = None,
    session: Session = Depends(get_session),
    hx_request: Optional[str] = Header(None, alias="HX-Request"),
):
    """Renderiza el tablón de avisos. Si la petición viene de HTMX,
    devuelve solo el fragmento parcial."""
    query = select(Aviso).where(Aviso.activo == True)  # noqa: E712

    if destino and destino.strip() != "":
        query = query.where(Aviso.destino == destino)

    avisos = session.exec(query).all()

    context = {
        "avisos": avisos,
        "destino_actual": destino,
    }

    # Petición HTMX: devolver solo el fragmento
    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="_lista_avisos.html",
            context=context,
        )

    # Petición normal: devolver la página completa
    return templates.TemplateResponse(
        request=request,
        name="avisos.html",
        context=context,
    )


# ---------------------------------------------------------------------------
# ENDPOINT API: Evaluación de avisos para el logon (POST /api/v1/evaluar-avisos)
# ---------------------------------------------------------------------------

@app.post("/api/v1/evaluar-avisos", response_model=RespuestaParaLogon)
def evaluar_avisos_cliente(
    payload: PeticionDeLogon,
    request: Request,
    session: Session = Depends(get_session),
):
    """Endpoint invocado por el script de inicio de sesión (AgenteSCAD.ps1).
    Evalúa qué avisos le corresponden al usuario/equipo y devuelve la URL
    para su visualización en el navegador.
    """
    # 1. Obtener los avisos aplicables
    avisos_vigentes = obtener_avisos_vigentes_para_cliente(
        session=session,
        usuario=payload.usuario,
        equipo=payload.equipo,
        grupos=payload.grupos,
    )

    if not avisos_vigentes:
        return RespuestaParaLogon(hay_avisos=False, total_avisos=0)

    # 2. Codificar la identidad en un token ligero para la URL
    token_data = {
        "usuario": payload.usuario,
        "equipo": payload.equipo,
        "grupos": payload.grupos,
    }
    token_encoded = base64.urlsafe_b64encode(
        json.dumps(token_data).encode()
    ).decode()

    # 3. Construir la URL del portal web
    base_url = str(request.base_url).rstrip("/")
    url_portal = f"{base_url}/portal-avisos?session_token={token_encoded}"

    return RespuestaParaLogon(
        hay_avisos=True,
        total_avisos=len(avisos_vigentes),
        url_portal=url_portal,
    )


# ---------------------------------------------------------------------------
# RUTA WEB: Portal de avisos para el navegador (GET /portal-avisos)
# ---------------------------------------------------------------------------

@app.get("/portal-avisos", response_class=HTMLResponse)
def mostrar_portal_avisos(
    session_token: str,
    request: Request,
    session: Session = Depends(get_session),
):
    """Decodifica el token de sesión, re-evalúa los avisos y los renderiza
    en la plantilla de tarjetas HTML."""
    try:
        raw_json = base64.urlsafe_b64decode(session_token.encode()).decode()
        datos_sesion = json.loads(raw_json)
    except Exception:
        return HTMLResponse(
            content="<h3>Error de sesión inválida</h3>",
            status_code=400,
        )

    usuario = datos_sesion.get("usuario", "")
    equipo = datos_sesion.get("equipo", "")
    grupos = datos_sesion.get("grupos", [])

    # Re-evaluar avisos para asegurar vigencia en el instante de carga
    avisos_vigentes = obtener_avisos_vigentes_para_cliente(
        session=session,
        usuario=usuario,
        equipo=equipo,
        grupos=grupos,
    )

    # Convertir el contenido Markdown de cada aviso a HTML
    avisos_renderizados = []
    for aviso in avisos_vigentes:
        aviso_dict = {
            "id": aviso.id,
            "titulo": aviso.titulo,
            "contenido_html": md_to_html(aviso.contenido_md),
            "importancia": aviso.importancia.value if hasattr(aviso, "importancia") and aviso.importancia else "media",
            "fecha_inicio": aviso.fecha_inicio,
        }
        avisos_renderizados.append(aviso_dict)

    return templates.TemplateResponse(
        request=request,
        name="portal_avisos.html",
        context={
            "usuario": usuario,
            "equipo": equipo,
            "avisos": avisos_renderizados,
        },
    )
