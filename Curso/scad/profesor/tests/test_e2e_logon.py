"""
Test de integración End-to-End: flujo completo logon → portal web.

Simula la llamada del script en el inicio de sesión y la posterior
apertura del navegador en el portal de avisos.
"""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from profesor.src.models import Aviso


def test_flujo_completo_logon_a_portal_web(client: TestClient, session: Session):
    ahora = datetime.now(timezone.utc)

    # 1. Crear avisos de prueba en la BD
    aviso_alumnos = Aviso(
        titulo="Mantenimiento de Red",
        contenido_md="El WiFi se cortará a las **17:00h**. Más info [aquí](https://ejemplo.local).",
        tipo_destino="grupo",
        destino="Alumnos",
        fecha_inicio=ahora - timedelta(minutes=5),
        activo=True,
        creado_por="admin",
    )
    session.add(aviso_alumnos)
    session.commit()

    # 2. PASO 1: El Agente Client hace POST enviando la identidad
    payload = {
        "usuario": "perez_m",
        "equipo": "AULA-01-PC02",
        "grupos": ["Alumnos", "Usuarios del Dominio"],
    }
    response_logon = client.post("/api/v1/evaluar-avisos", json=payload)
    assert response_logon.status_code == 200
    data = response_logon.json()
    assert data["hay_avisos"] is True
    assert data["total_avisos"] == 1
    assert "url_portal" in data

    # 3. PASO 2: El Navegador abre la URL devuelta
    url_portal = data["url_portal"]
    path_portal = url_portal.split("http://testserver")[-1]
    response_portal = client.get(path_portal)
    assert response_portal.status_code == 200
    assert "text/html" in response_portal.headers["content-type"]

    # Validar que el HTML renderizado contiene las tarjetas y el Markdown
    html = response_portal.text
    assert "Mantenimiento de Red" in html
    assert "<strong>17:00h</strong>" in html or "<b>17:00h</b>" in html
    assert 'href="https://ejemplo.local"' in html


def test_logon_sin_avisos_devuelve_false(client: TestClient):
    payload = {
        "usuario": "nuevo",
        "equipo": "PC-SIN-AVISOS",
        "grupos": [],
    }
    response = client.post("/api/v1/evaluar-avisos", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["hay_avisos"] is False
    assert data["total_avisos"] == 0
