"""
Script de poblacion de la base de datos scad.db.

Inserta al menos 10 registros en cada tabla (Aviso y LogActividad).
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from profesor.src.models import (
    Aviso,
    ImportanciaEnum,
    LogActividad,
    TipoDestinoEnum,
    crear_db_y_tablas,
    engine,
)


def poblar_avisos(session: Session):
    ahora = datetime.now(timezone.utc)

    avisos = [
        Aviso(
            titulo="Mantenimiento programado del servidor DC01",
            contenido_md="El controlador de dominio **SRV-DC01** se reiniciara el **domingo a las 04:00h**. Guardad vuestro trabajo.",
            tipo_destino=TipoDestinoEnum.TODOS,
            destino="TODOS",
            fecha_inicio=ahora - timedelta(hours=2),
            fecha_fin=ahora + timedelta(days=7),
            activo=True,
            creado_por="admin_dom",
            importancia=ImportanciaEnum.ALTA,
        ),
        Aviso(
            titulo="Cambio de contrasena obligatorio",
            contenido_md="Por politicas de seguridad, todos los usuarios deben cambiar su contrasena antes del **viernes**. Usa `Ctrl+Alt+Supr > Cambiar contrasena`.",
            tipo_destino=TipoDestinoEnum.TODOS,
            destino="TODOS",
            fecha_inicio=ahora - timedelta(days=1),
            activo=True,
            creado_por="admin_dom",
            importancia=ImportanciaEnum.CRITICA,
        ),
        Aviso(
            titulo="Actualizacion de antivirus en equipos del aula 101",
            contenido_md="Se desplegara la actualizacion del antivirus en los equipos del **Aula 101**. No apagueis los PCs al final de la jornada.",
            tipo_destino=TipoDestinoEnum.EQUIPO,
            destino="PC-AULA101-01",
            fecha_inicio=ahora - timedelta(hours=5),
            activo=True,
            creado_por="soporte_dom",
            importancia=ImportanciaEnum.MEDIA,
        ),
        Aviso(
            titulo="Corte de WiFi por mantenimiento de red",
            contenido_md="El acceso WiFi estara interrumpido de **17:00h a 18:00h**. Conectaos por cable si es necesario. Mas info [aqui](https://intranet.empresa.local/mantenimiento).",
            tipo_destino=TipoDestinoEnum.GRUPO,
            destino="Alumnos",
            fecha_inicio=ahora - timedelta(minutes=30),
            activo=True,
            creado_por="admin_dom",
            importancia=ImportanciaEnum.ALTA,
        ),
        Aviso(
            titulo="Reunion de claustro para profesores",
            contenido_md="Recordatorio: reunion de claustro el **martes a las 16:00h** en la sala de juntas. Traed los informes de evaluacion.",
            tipo_destino=TipoDestinoEnum.GRUPO,
            destino="Docentes",
            fecha_inicio=ahora - timedelta(hours=1),
            activo=True,
            creado_por="admin_dom",
            importancia=ImportanciaEnum.MEDIA,
        ),
        Aviso(
            titulo="Nuevo software disponible: Python 3.12",
            contenido_md="Se ha instalado **Python 3.12** y **uv** en todos los equipos del laboratorio. Recordad ejecutar `uv sync` para configurar el entorno.",
            tipo_destino=TipoDestinoEnum.GRUPO,
            destino="Alumnos",
            fecha_inicio=ahora - timedelta(days=3),
            activo=True,
            creado_por="soporte_dom",
            importancia=ImportanciaEnum.BAJA,
        ),
        Aviso(
            titulo="Aviso individual para jgarcia",
            contenido_md="Tu solicitud de ampliacion de cuota de almacenamiento ha sido aprobada. Ya tienes **5GB** adicionales en tu cuenta.",
            tipo_destino=TipoDestinoEnum.USUARIO,
            destino="jgarcia",
            fecha_inicio=ahora - timedelta(hours=10),
            activo=True,
            creado_por="soporte_dom",
            importancia=ImportanciaEnum.BAJA,
        ),
        Aviso(
            titulo="Mantenimiento del equipo SRV-DC02",
            contenido_md="El servidor secundario **SRV-DC02** estara en mantenimiento el proximo miercoles. Los servicios de autenticacion pasaran al primario.",
            tipo_destino=TipoDestinoEnum.EQUIPO,
            destino="SRV-DC02",
            fecha_inicio=ahora + timedelta(days=1),
            activo=True,
            creado_por="admin_dom",
            importancia=ImportanciaEnum.ALTA,
        ),
        Aviso(
            titulo="Inventario de hardware pendiente",
            contenido_md="Se realizara un inventario de hardware en la **OU de Aulas**. Etiquetad los equipos sin inventariar con la pegatina correspondiente.",
            tipo_destino=TipoDestinoEnum.OU,
            destino="OU-AULAS",
            fecha_inicio=ahora - timedelta(days=2),
            fecha_fin=ahora + timedelta(days=14),
            activo=True,
            creado_por="soporte_dom",
            importancia=ImportanciaEnum.MEDIA,
        ),
        Aviso(
            titulo="Aviso caducado - Fin de curso anterior",
            contenido_md="Las cuentas de los alumnos de la promocion anterior seran deshabilitadas el 30 de junio.",
            tipo_destino=TipoDestinoEnum.TODOS,
            destino="TODOS",
            fecha_inicio=ahora - timedelta(days=120),
            fecha_fin=ahora - timedelta(days=60),
            activo=True,
            creado_por="admin_dom",
            importancia=ImportanciaEnum.MEDIA,
        ),
        Aviso(
            titulo="Backup de perfiles en OU-ADMIN",
            contenido_md="Se realizara un backup de los perfiles roaming de la **OU de Administracion** durante el fin de semana.",
            tipo_destino=TipoDestinoEnum.OU,
            destino="OU-ADMIN",
            fecha_inicio=ahora - timedelta(hours=8),
            activo=True,
            creado_por="admin_dom",
            importancia=ImportanciaEnum.BAJA,
        ),
        Aviso(
            titulo="Mensaje personal para mlopez",
            contenido_md="Tu equipo ha sido asignado al grupo **Desarrollo**. Reinicia la sesion para que los cambios de grupo surtan efecto.",
            tipo_destino=TipoDestinoEnum.USUARIO,
            destino="mlopez",
            fecha_inicio=ahora - timedelta(minutes=45),
            activo=True,
            creado_por="soporte_dom",
            importancia=ImportanciaEnum.MEDIA,
        ),
    ]

    session.add_all(avisos)
    session.commit()
    print(f"  {len(avisos)} avisos insertados.")


def poblar_logs(session: Session):
    ahora = datetime.now(timezone.utc)

    logs = [
        LogActividad(
            usuario_admin="admin_dom",
            accion="CREAR_AVISO",
            detalle="Creado aviso ID 1: 'Mantenimiento programado del servidor DC01'",
            timestamp=ahora - timedelta(hours=2),
        ),
        LogActividad(
            usuario_admin="admin_dom",
            accion="CREAR_AVISO",
            detalle="Creado aviso ID 2: 'Cambio de contrasena obligatorio'",
            timestamp=ahora - timedelta(days=1),
        ),
        LogActividad(
            usuario_admin="soporte_dom",
            accion="CREAR_AVISO",
            detalle="Creado aviso ID 3: 'Actualizacion de antivirus en equipos del aula 101'",
            timestamp=ahora - timedelta(hours=5),
        ),
        LogActividad(
            usuario_admin="admin_dom",
            accion="CREAR_AVISO",
            detalle="Creado aviso ID 4: 'Corte de WiFi por mantenimiento de red'",
            timestamp=ahora - timedelta(minutes=30),
        ),
        LogActividad(
            usuario_admin="admin_dom",
            accion="DESACTIVAR_AVISO",
            detalle="Desactivado aviso ID 10: 'Aviso caducado - Fin de curso anterior'",
            timestamp=ahora - timedelta(days=60),
        ),
        LogActividad(
            usuario_admin="soporte_dom",
            accion="CREAR_AVISO",
            detalle="Creado aviso ID 6: 'Nuevo software disponible: Python 3.12'",
            timestamp=ahora - timedelta(days=3),
        ),
        LogActividad(
            usuario_admin="soporte_dom",
            accion="MODIFICAR_AVISO",
            detalle="Modificado aviso ID 7: ampliacion de cuota aprobada para jgarcia",
            timestamp=ahora - timedelta(hours=10),
        ),
        LogActividad(
            usuario_admin="admin_dom",
            accion="CREAR_AVISO",
            detalle="Creado aviso ID 8: 'Mantenimiento del equipo SRV-DC02'",
            timestamp=ahora + timedelta(days=1),
        ),
        LogActividad(
            usuario_admin="soporte_dom",
            accion="CREAR_AVISO",
            detalle="Creado aviso ID 9: 'Inventario de hardware pendiente'",
            timestamp=ahora - timedelta(days=2),
        ),
        LogActividad(
            usuario_admin="admin_dom",
            accion="INICIO_SESION",
            detalle="Inicio de sesion del administrador admin_dom desde 192.168.1.50",
            timestamp=ahora - timedelta(hours=2),
        ),
        LogActividad(
            usuario_admin="soporte_dom",
            accion="INICIO_SESION",
            detalle="Inicio de sesion del administrador soporte_dom desde 192.168.1.51",
            timestamp=ahora - timedelta(hours=5),
        ),
        LogActividad(
            usuario_admin="admin_dom",
            accion="ELIMINAR_AVISO",
            detalle="Eliminado aviso ID 99 (datos de prueba obsoletos)",
            timestamp=ahora - timedelta(days=7),
        ),
    ]

    session.add_all(logs)
    session.commit()
    print(f"  {len(logs)} registros de log insertados.")


if __name__ == "__main__":
    print("Creando tablas si no existen...")
    crear_db_y_tablas()

    with Session(engine) as session:
        print("Poblando tabla Aviso...")
        poblar_avisos(session)
        print("Poblando tabla LogActividad...")
        poblar_logs(session)

    print("Base de datos scad.db poblada correctamente.")
