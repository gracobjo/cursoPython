"""
Modelos de datos SQLModel para SCAD (versión alumno).

Define las tablas de la base de datos SQLite y los esquemas DTO.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Session, create_engine


# ---------------------------------------------------------------------------
# Enumeraciones
# ---------------------------------------------------------------------------

class TipoDestinoEnum(str, Enum):
    """Tipos de destino permitidos en el Active Directory."""
    TODOS = "todos"
    USUARIO = "usuario"
    EQUIPO = "equipo"
    GRUPO = "grupo"
    OU = "ou"


class ImportanciaEnum(str, Enum):
    """Niveles de importancia de un aviso."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


# ---------------------------------------------------------------------------
# Modelo base y de tabla
# ---------------------------------------------------------------------------

class AvisoBase(SQLModel):
    """Campos comunes compartidos entre la BD y los DTOs."""
    titulo: str = Field(min_length=3, max_length=100)
    contenido_md: str
    tipo_destino: TipoDestinoEnum
    destino: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    activo: bool = True
    importancia: ImportanciaEnum = Field(default=ImportanciaEnum.MEDIA)


class Aviso(AvisoBase, table=True):
    """Modelo principal: representa un aviso en la base de datos."""
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    creado_por: str
    creado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    modificado_por: Optional[str] = None
    modificado_en: Optional[datetime] = None


class LogActividad(SQLModel, table=True):
    """Registro de auditoría: historial de acciones de administradores."""
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    usuario_admin: str
    accion: str
    detalle: str


# ---------------------------------------------------------------------------
# DTOs (Data Transfer Objects)
# ---------------------------------------------------------------------------

class AvisoCreate(AvisoBase):
    """Datos requeridos para crear un aviso (sin id ni fechas de auditoría)."""
    pass


class AvisoUpdate(SQLModel):
    """Campos opcionales para actualizaciones parciales (PATCH)."""
    titulo: Optional[str] = None
    contenido_md: Optional[str] = None
    tipo_destino: Optional[TipoDestinoEnum] = None
    destino: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    activo: Optional[bool] = None
    importancia: Optional[ImportanciaEnum] = None


# ---------------------------------------------------------------------------
# Configuración del motor de base de datos SQLite
# ---------------------------------------------------------------------------

sqlite_file_name = "scad.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)


def crear_db_y_tablas():
    """Crea las tablas en el archivo scad.db si no existen."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Inyección de dependencia: entrega una sesión de BD por petición."""
    with Session(engine) as session:
        yield session
