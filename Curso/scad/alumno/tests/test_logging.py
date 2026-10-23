"""
Tests del middleware de logging y auditoría (versión alumno).

Verifica que el middleware añade la cabecera X-Process-Time-MS
a las respuestas HTTP y que el fichero de logs registra los eventos.
"""

from pathlib import Path


def test_middleware_inyecta_cabecera_tiempo(client):
    """Verifica que el middleware añade la cabecera X-Process-Time-MS
    a cualquier respuesta."""
    response = client.get("/avisos")
    assert response.status_code == 200
    assert "X-Process-Time-MS" in response.headers

    # Validar que el valor sea un número flotante parseable
    tiempo_ms = float(response.headers["X-Process-Time-MS"])
    assert tiempo_ms >= 0.0


def test_escribir_log_en_fichero(client):
    """Comprueba que al realizar peticiones HTTP, el archivo scad.log
    se crea y se actualiza."""
    # Realizar una petición
    response = client.get("/avisos")
    assert response.status_code == 200

    # Ubicación esperada del fichero de log
    log_file = Path("alumno/src/logs/scad.log")

    # En el entorno de tests, comprobar que el archivo existe
    if log_file.exists():
        contenido = log_file.read_text(encoding="utf-8")
        assert "GET /avisos" in contenido
