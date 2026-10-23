"""
Tests de los modelos SQLModel.

Verifica la creación de tablas y operaciones básicas usando una
base de datos SQLite en memoria para no alterar la BD real.
"""

from datetime import datetime, timezone

from sqlmodel import Session, SQLModel, create_engine, select

from alumno.src.models import Aviso, LogActividad, TipoDestinoEnum


def test_creacion_tablas_y_modelos_en_memoria():
    # Usamos una base de datos SQLite en memoria para no alterar la BD real
    engine_test = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine_test)

    with Session(engine_test) as session:
        # 1. Crear un aviso de prueba
        aviso = Aviso(
            titulo="Aviso de Prueba",
            contenido_md="# Titulo\nMensaje en Markdown",
            tipo_destino=TipoDestinoEnum.GRUPO,
            destino="Sistemas",
            fecha_inicio=datetime.now(timezone.utc),
            creado_por="admin_test",
        )
        session.add(aviso)
        session.commit()
        session.refresh(aviso)

        # Comprobar que SQLite asignó automáticamente el id = 1
        assert aviso.id is not None
        assert aviso.id == 1
        assert aviso.activo is True
        assert aviso.destino == "Sistemas"

        # 2. Consultar el aviso recién guardado
        aviso_db = session.exec(
            select(Aviso).where(Aviso.id == 1)
        ).first()
        assert aviso_db is not None
        assert aviso_db.titulo == "Aviso de Prueba"


def test_creacion_log_actividad():
    engine_test = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine_test)

    with Session(engine_test) as session:
        log = LogActividad(
            usuario_admin="soporte_dom",
            accion="CREAR_AVISO",
            detalle="Se ha creado el aviso ID 1",
        )
        session.add(log)
        session.commit()
        session.refresh(log)

        assert log.id == 1
        assert log.usuario_admin == "soporte_dom"


def test_valores_por_defecto_del_aviso():
    engine_test = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine_test)

    with Session(engine_test) as session:
        aviso = Aviso(
            titulo="Aviso Default",
            contenido_md="Contenido",
            tipo_destino=TipoDestinoEnum.USUARIO,
            destino="jgarcia",
            fecha_inicio=datetime.now(timezone.utc),
            creado_por="admin",
        )
        session.add(aviso)
        session.commit()
        session.refresh(aviso)

        # activo debe ser True por defecto
        assert aviso.activo is True
        # creado_en debe tener un valor (generado por default_factory)
        assert aviso.creado_en is not None
        # modificado_por debe ser None inicialmente
        assert aviso.modificado_por is None
