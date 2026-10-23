"""
Tests del motor de evaluación de avisos.

Verifica el algoritmo de vigencia temporal y el filtrado por
destinatario (usuario, equipo, grupo, todos).
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from profesor.src.evaluador import obtener_avisos_vigentes_para_cliente
from profesor.src.models import Aviso


def test_evaluacion_vigencia_y_destinatarios(session: Session):
    ahora = datetime.now(timezone.utc)

    # 1. Aviso General (Vigente)
    a_general = Aviso(
        titulo="Aviso General",
        contenido_md="Hola a todos",
        tipo_destino="todos",
        destino="TODOS",
        fecha_inicio=ahora - timedelta(hours=1),
        activo=True,
        creado_por="admin",
    )

    # 2. Aviso Caducado (No debe aparecer)
    a_caducado = Aviso(
        titulo="Aviso Antiguo",
        contenido_md="Expirado",
        tipo_destino="todos",
        destino="TODOS",
        fecha_inicio=ahora - timedelta(days=2),
        fecha_fin=ahora - timedelta(days=1),
        activo=True,
        creado_por="admin",
    )

    # 3. Aviso Específico para Grupo "Docentes"
    a_grupo = Aviso(
        titulo="Reunión Claustro",
        contenido_md="Aviso para profesores",
        tipo_destino="grupo",
        destino="Docentes",
        fecha_inicio=ahora - timedelta(minutes=10),
        activo=True,
        creado_por="admin",
    )

    # 4. Aviso para otro equipo
    a_equipo_otro = Aviso(
        titulo="Mantenimiento Aula 200",
        contenido_md="Solo Aula 200",
        tipo_destino="equipo",
        destino="AULA-200-PC01",
        fecha_inicio=ahora - timedelta(minutes=10),
        activo=True,
        creado_por="admin",
    )

    session.add_all([a_general, a_caducado, a_grupo, a_equipo_otro])
    session.commit()

    # EJECUCIÓN: Petición desde un PC del Aula 101 por un usuario del grupo "Docentes"
    resultado = obtener_avisos_vigentes_para_cliente(
        session=session,
        usuario="jgarcia",
        equipo="AULA-101-PC05",
        grupos=["docentes", "usuarios del dominio"],
        momento=ahora,
    )

    titulos_obtenidos = [a.titulo for a in resultado]

    # COMPROBACIONES
    assert "Aviso General" in titulos_obtenidos
    assert "Reunión Claustro" in titulos_obtenidos
    assert "Aviso Antiguo" not in titulos_obtenidos
    assert "Mantenimiento Aula 200" not in titulos_obtenidos
    assert len(resultado) == 2


def test_aviso_inactivo_no_aparece(session: Session):
    ahora = datetime.now(timezone.utc)
    a_inactivo = Aviso(
        titulo="Aviso Desactivado",
        contenido_md="No debería verse",
        tipo_destino="todos",
        destino="TODOS",
        fecha_inicio=ahora - timedelta(hours=1),
        activo=False,
        creado_por="admin",
    )
    session.add(a_inactivo)
    session.commit()

    resultado = obtener_avisos_vigentes_para_cliente(
        session=session,
        usuario="test_user",
        equipo="PC-TEST",
        grupos=[],
        momento=ahora,
    )
    assert all(r.titulo != "Aviso Desactivado" for r in resultado)


def test_aviso_por_usuario_especifico(session: Session):
    ahora = datetime.now(timezone.utc)
    a_usuario = Aviso(
        titulo="Aviso Personal",
        contenido_md="Solo para jgarcia",
        tipo_destino="usuario",
        destino="jgarcia",
        fecha_inicio=ahora - timedelta(minutes=5),
        activo=True,
        creado_por="admin",
    )
    session.add(a_usuario)
    session.commit()

    # Coincide
    resultado = obtener_avisos_vigentes_para_cliente(
        session=session,
        usuario="jgarcia",
        equipo="PC-01",
        grupos=[],
        momento=ahora,
    )
    assert len(resultado) == 1
    assert resultado[0].titulo == "Aviso Personal"

    # No coincide (otro usuario)
    resultado_otro = obtener_avisos_vigentes_para_cliente(
        session=session,
        usuario="otro_usuario",
        equipo="PC-01",
        grupos=[],
        momento=ahora,
    )
    assert len(resultado_otro) == 0
