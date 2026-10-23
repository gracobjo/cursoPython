"""
Módulo de autenticación HTTP Basic para administradores de dominio.

En producción se conectaría con Active Directory / LDAP.
Para el curso se simulan dos usuarios administradores.
"""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Instancia del esquema de seguridad HTTP Basic
security = HTTPBasic()

# Usuarios administradores simulados del dominio
ADMIN_USERS = {
    "admin_dom": "P@ssw0rd2026",
    "soporte_dom": "AdminSCAD123",
}


def obtener_usuario_admin_actual(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    """
    Dependencia de seguridad que valida la autenticación HTTP Basic.

    Devuelve el nombre del usuario autenticado si las credenciales son
    correctas, o lanza HTTP 401 en caso contrario.
    """
    usuario_correcto = False
    if credentials.username in ADMIN_USERS:
        password_almacenada = ADMIN_USERS[credentials.username]
        # compare_digest evita ataques de temporización al comparar cadenas
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
