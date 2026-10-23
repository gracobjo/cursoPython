from fastapi.testclient import TestClient
from main import app

#Create a TestClient instance for testing the FastAPI application
client = TestClient(app)

def test_ruta_inicio():
    # Send a GET request to the root endpoint
    response = client.get("/")
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Assert that the response JSON matches the expected output
    assert response.json()["message"] == {"message": "Bienvenido a la API de FastAPI!"}

def test_ruta_agenda():
    response = client.get("/app")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!doctype html>" in response.text.lower()
    assert "<title>Agenda de tareas</title>" in response.text


def test_botones_agenda():
    response = client.get("/static/js/agenda.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]

    for button in (
        'id: "pending-tab"',
        'id: "all-tab"',
        'id: "refresh-button"',
        'id: "submit-button"',
        '"Pendientes"',
        '"Todas"',
        '"↻ Actualizar agenda"',
        '"Crear tarea"',
    ):
        assert button in response.text


def test_agenda_js_genera_dom_sin_inner_html():
    response = client.get("/static/js/agenda.js")

    assert response.status_code == 200
    assert "innerHTML" not in response.text
    assert "document.createElement" in response.text
    assert "appendChild" in response.text