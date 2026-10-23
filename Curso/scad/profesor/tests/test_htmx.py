"""
Tests de integración con HTMX.

Verifica que FastAPI responde con el fragmento parcial cuando la
petición incluye la cabecera HX-Request.
"""

from datetime import datetime, timezone


def test_filtro_htmx_devuelve_fragmento_parcial(client):
    """Verifica que al enviar la cabecera HX-Request solo se
    renderice el fragmento del HTML."""
    # 1. Crear avisos con distintos destinos
    payload1 = {
        "titulo": "Aviso General",
        "contenido_md": "Contenido 1",
        "tipo_destino": "grupo",
        "destino": "TODOS",
        "fecha_inicio": datetime.now(timezone.utc).isoformat(),
        "activo": True,
    }
    payload2 = {
        "titulo": "Aviso Aula 101",
        "contenido_md": "Contenido 2",
        "tipo_destino": "equipo",
        "destino": "AULA_101",
        "fecha_inicio": datetime.now(timezone.utc).isoformat(),
        "activo": True,
    }

    client.post("/avisos", json=payload1, auth=("admin_dom", "P@ssw0rd2026"))
    client.post("/avisos", json=payload2, auth=("admin_dom", "P@ssw0rd2026"))

    # 2. Petición HTMX filtrando por AULA_101
    headers = {"HX-Request": "true"}
    response = client.get("/?destino=AULA_101", headers=headers)

    assert response.status_code == 200
    # Debe incluir la tarjeta filtrada
    assert "Aviso Aula 101" in response.text
    # No debe incluir la estructura global completa
    assert "<!DOCTYPE html>" not in response.text
    assert "<header>" not in response.text


def test_peticion_normal_devuelve_pagina_completa(client):
    """Sin cabecera HX-Request se devuelve la página completa."""
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "<header>" in response.text
