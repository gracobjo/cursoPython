"""
Tests del CRUD de avisos (versión alumno).

Verifica el ciclo de vida completo de un aviso:
Creación → Consulta → Edición → Eliminación.

Usa el cliente de pruebas con la dependencia get_session
sobrescrita para apuntar a una BD SQLite en memoria.
"""


def test_crear_y_leer_aviso(client):
    # 1. Crear un aviso via POST (con autenticación)
    payload = {
        "titulo": "Mantenimiento Servidor AD",
        "contenido_md": "El servidor se reiniciara a las 22:00",
        "tipo_destino": "equipo",
        "destino": "SRV-DC01",
        "fecha_inicio": "2026-03-30T22:00:00Z",
        "activo": True,
    }
    response = client.post(
        "/avisos", json=payload, auth=("admin_dom", "P@ssw0rd2026")
    )
    assert response.status_code == 201
    datos = response.json()
    assert datos["id"] is not None
    assert datos["titulo"] == "Mantenimiento Servidor AD"
    aviso_id = datos["id"]

    # 2. Obtener el aviso recién creado via GET
    response_get = client.get(f"/avisos/{aviso_id}")
    assert response_get.status_code == 200
    assert response_get.json()["destino"] == "SRV-DC01"


def test_actualizar_aviso_patch(client):
    # Crear un aviso inicial
    payload = {
        "titulo": "Aviso Temporal",
        "contenido_md": "Contenido inicial",
        "tipo_destino": "usuario",
        "destino": "mlopez",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    res_crear = client.post(
        "/avisos", json=payload, auth=("admin_dom", "P@ssw0rd2026")
    )
    aviso_id = res_crear.json()["id"]

    # Desactivar el aviso via PATCH
    res_patch = client.patch(
        f"/avisos/{aviso_id}",
        json={"activo": False},
        auth=("admin_dom", "P@ssw0rd2026"),
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["activo"] is False
    assert res_patch.json()["modificado_por"] == "admin_dom"


def test_eliminar_aviso_delete(client):
    # Crear aviso
    payload = {
        "titulo": "Aviso a borrar",
        "contenido_md": "Borrar pronto",
        "tipo_destino": "grupo",
        "destino": "Ventas",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    res_crear = client.post(
        "/avisos", json=payload, auth=("admin_dom", "P@ssw0rd2026")
    )
    aviso_id = res_crear.json()["id"]

    # Eliminar aviso (con autenticación)
    res_del = client.delete(
        f"/avisos/{aviso_id}", auth=("admin_dom", "P@ssw0rd2026")
    )
    assert res_del.status_code == 204

    # Verificar que ya no existe (404)
    res_get = client.get(f"/avisos/{aviso_id}")
    assert res_get.status_code == 404


def test_listar_avisos_filtrado(client):
    # Crear dos avisos con destinos distintos
    payload1 = {
        "titulo": "Aviso para ventas",
        "contenido_md": "Contenido 1",
        "tipo_destino": "grupo",
        "destino": "Ventas",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    payload2 = {
        "titulo": "Aviso para IT",
        "contenido_md": "Contenido 2",
        "tipo_destino": "grupo",
        "destino": "IT",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    client.post("/avisos", json=payload1, auth=("admin_dom", "P@ssw0rd2026"))
    client.post("/avisos", json=payload2, auth=("admin_dom", "P@ssw0rd2026"))

    # Listar todos
    response_all = client.get("/avisos")
    assert response_all.status_code == 200
    assert len(response_all.json()) == 2

    # Filtrar por destino
    response_filtrado = client.get("/avisos?destino=Ventas")
    assert response_filtrado.status_code == 200
    assert len(response_filtrado.json()) == 1
    assert response_filtrado.json()[0]["destino"] == "Ventas"
