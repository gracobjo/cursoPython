"""
Motor de evaluación de avisos para SCAD.

Evalúa la identidad de la máquina/usuario (usuario, equipo, grupos de AD)
y las fechas de vigencia para entregar únicamente los avisos aplicables.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session, select, or_

from profesor.src.models import Aviso


def obtener_avisos_vigentes_para_cliente(
    session: Session,
    usuario: str,
    equipo: str,
    grupos: Optional[List[str]] = None,
    momento: Optional[datetime] = None,
) -> List[Aviso]:
    """
    Evalúa y devuelve la lista de avisos activos y vigentes aplicables a un
    usuario, equipo y conjunto de grupos de Active Directory específicos.

    Reglas de vigencia temporal:
    1. activo == True
    2. fecha_inicio <= ahora (el aviso ya ha comenzado)
    3. fecha_fin is None O fecha_fin >= ahora (no ha caducado)

    Reglas de destinatario:
    - tipo "todos":  coincide con cualquier usuario/equipo
    - tipo "usuario": coincide si el usuario solicitante es exactamente ese
    - tipo "equipo":  coincide si el equipo solicitante es exactamente ese
    - tipo "grupo":   coincide si el destino está en la lista de grupos del usuario
    """
    if momento is None:
        momento = datetime.now(timezone.utc)
    if grupos is None:
        grupos = []

    # Normalizamos para evitar fallos de coincidencia por mayúsculas/minúsculas
    usuario_clean = usuario.strip().lower()
    equipo_clean = equipo.strip().upper()
    grupos_clean = [g.strip().lower() for g in grupos]

    # 1. Cargar avisos activos con filtro de vigencia temporal
    query = select(Aviso).where(
        Aviso.activo == True,  # noqa: E712
        Aviso.fecha_inicio <= momento,
        or_(Aviso.fecha_fin == None, Aviso.fecha_fin >= momento),  # noqa: E711
    )
    candidatos = session.exec(query).all()

    # 2. Filtrar en memoria por algoritmo de destinatario
    avisos_evaluados = []
    for aviso in candidatos:
        tipo = aviso.tipo_destino.value.lower()
        destino = aviso.destino.strip()

        if tipo == "todos" or destino.upper() == "TODOS":
            avisos_evaluados.append(aviso)
        elif tipo == "usuario" and destino.lower() == usuario_clean:
            avisos_evaluados.append(aviso)
        elif tipo == "equipo" and destino.upper() == equipo_clean:
            avisos_evaluados.append(aviso)
        elif tipo == "grupo" and destino.lower() in grupos_clean:
            avisos_evaluados.append(aviso)

    return avisos_evaluados
