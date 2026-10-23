"""
Tests de las rutas básicas de SCAD (versión alumno).

Verifica las rutas GET /, /version, /equipo-desarrollo,
/info-dominio y el comportamiento 404.
"""

from datetime import datetime, timezone


def test_ruta_inicio_devuelve_html(client):
    """La ruta principal devuelve código 200 y contenido HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "SCAD" in response.text


def test_ruta_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    datos = response.json()
    assert datos["app"] == "SCAD"
    assert datos["version"] == "1.0.0"
    assert "organizacion" in datos


def test_ruta_equipo_desarrollo(client):
    response = client.get("/equipo-desarrollo")
    assert response.status_code == 200
    datos = response.json()
    assert isinstance(datos["equipo"], list)
    assert len(datos["equipo"]) == 3


def test_ruta_info_dominio(client):
    response = client.get("/info-dominio")
    assert response.status_code == 200
    datos = response.json()
    assert "nombre_dominio" in datos
    assert "servidor_dc" in datos
    assert "estado_dc" in datos


def test_ruta_no_existente(client):
    # Comprobar que una ruta que no existe devuelve un error 404
    response = client.get("/ruta-falsa")
    assert response.status_code == 404


def test_renderizado_contenido_markdown(client):
    """Comprueba que el contenido en Markdown se convierte a HTML."""
    payload = {
        "titulo": "Aviso con Formato",
        "contenido_md": "**Atencion:** Servidor en *mantenimiento*",
        "tipo_destino": "grupo",
        "destino": "TODOS",
        "fecha_inicio": datetime.now(timezone.utc).isoformat(),
        "activo": True,
    }
    # Crear el aviso (necesita autenticación)
    response_post = client.post(
        "/avisos",
        json=payload,
        auth=("admin_dom", "P@ssw0rd2026"),
    )
    assert response_post.status_code in (200, 201), (
        f"Error al crear aviso: {response_post.json()}"
    )

    # Consultar la vista HTML
    response = client.get("/")
    assert response.status_code == 200

    # Validar el renderizado del filtro Markdown
    assert "<strong>Atencion:</strong>" in response.text
    assert "<em>mantenimiento</em>" in response.text
