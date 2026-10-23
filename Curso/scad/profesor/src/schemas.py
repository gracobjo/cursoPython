"""
Esquemas Pydantic para la comunicación con el agente cliente (logon).

El script de inicio de sesión envía la identidad del usuario/equipo
y la API responde indicando si hay avisos y la URL del portal web.
"""

from typing import List, Optional

from pydantic import BaseModel


class PeticionDeLogon(BaseModel):
    """Payload enviado por el logon.cmd al iniciar sesión."""
    usuario: str
    equipo: str
    grupos: List[str] = []


class RespuestaParaLogon(BaseModel):
    """Respuesta enviada de vuelta al logon.cmd."""
    hay_avisos: bool
    total_avisos: int
    url_portal: Optional[str] = None
