"""
Tests de seguridad para SCAD (versión alumno).

Verifica los accesos autorizados y denegados mediante
HTTP Basic Authentication.
"""


# 1. Test de lectura pública (Sin necesidad de autenticación)
def test_lectura_avisos_publica(client):
    response = client.get("/avisos")
    assert response.status_code == 200


# 2. Test de intento de creación SIN credenciales (Debe fallar con 401)
def test_crear_aviso_sin_autenticacion_falla(client):
    payload = {
        "titulo": "Intento no autorizado",
        "contenido_md": "Contenido",
        "tipo_destino": "usuario",
        "destino": "jgarcia",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    response = client.post("/avisos", json=payload)
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


# 3. Test de intento de creación con CREDENCIALES INCORRECTAS (401)
def test_crear_aviso_credenciales_erroneas_falla(client):
    payload = {
        "titulo": "Intento con clave falsa",
        "contenido_md": "Contenido",
        "tipo_destino": "usuario",
        "destino": "jgarcia",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    response = client.post(
        "/avisos",
        json=payload,
        auth=("admin_dom", "clave_incorrecta"),
    )
    assert response.status_code == 401


# 4. Test de creación CON CREDENCIALES CORRECTAS (Debe tener éxito 201)
def test_crear_aviso_autenticado_exito(client):
    payload = {
        "titulo": "Aviso de Seguridad Crítico",
        "contenido_md": "Cambio de contraseñas de dominio obligatorias",
        "tipo_destino": "grupo",
        "destino": "Todos_Los_Usuarios",
        "fecha_inicio": "2026-03-30T08:00:00Z",
    }
    response = client.post(
        "/avisos",
        json=payload,
        auth=("admin_dom", "P@ssw0rd2026"),
    )
    assert response.status_code == 201
    datos = response.json()
    assert datos["creado_por"] == "admin_dom"


# 5. Test de PATCH sin credenciales (Debe fallar con 401)
def test_actualizar_aviso_sin_autenticacion_falla(client):
    # Crear un aviso primero
    payload = {
        "titulo": "Aviso para editar",
        "contenido_md": "Contenido",
        "tipo_destino": "usuario",
        "destino": "jgarcia",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    res = client.post(
        "/avisos", json=payload, auth=("admin_dom", "P@ssw0rd2026")
    )
    aviso_id = res.json()["id"]

    # Intentar PATCH sin credenciales
    response = client.patch(f"/avisos/{aviso_id}", json={"activo": False})
    assert response.status_code == 401


# 6. Test de DELETE sin credenciales (Debe fallar con 401)
def test_eliminar_aviso_sin_autenticacion_falla(client):
    payload = {
        "titulo": "Aviso para borrar",
        "contenido_md": "Contenido",
        "tipo_destino": "usuario",
        "destino": "jgarcia",
        "fecha_inicio": "2026-03-30T10:00:00Z",
    }
    res = client.post(
        "/avisos", json=payload, auth=("admin_dom", "P@ssw0rd2026")
    )
    aviso_id = res.json()["id"]

    response = client.delete(f"/avisos/{aviso_id}")
    assert response.status_code == 401
