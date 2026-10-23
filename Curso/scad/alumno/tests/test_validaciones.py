"""
Tests del endpoint /validar-destino.

Verifica los casos exitosos y los casos de error de validación
de destinos del dominio (usuario, equipo, grupo, ou).
"""


# 1. Test de éxito para usuario
def test_validar_destino_usuario_exito(client):
    payload = {
        "tipo_destino": "usuario",
        "nombre_destino": "jgarcia",
    }
    response = client.post("/validar-destino", json=payload)
    assert response.status_code == 200
    assert response.json() == {
        "valido": True,
        "destino": "usuario:jgarcia",
    }


# 2. Test de éxito para equipo correcto
def test_validar_destino_equipo_exito(client):
    payload = {
        "tipo_destino": "equipo",
        "nombre_destino": "PC-AULA101",
    }
    response = client.post("/validar-destino", json=payload)
    assert response.status_code == 200
    assert response.json()["destino"] == "equipo:PC-AULA101"


# 3. Test de error de negocio (Equipo con nombre incorrecto)
def test_validar_destino_equipo_nombre_invalido(client):
    payload = {
        "tipo_destino": "equipo",
        "nombre_destino": "LAPTOP-JUAN",
    }
    response = client.post("/validar-destino", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Los nombres de equipo deben empezar por PC- o SRV-"
    )


# 4. Test de error de Pydantic (Tipo de destino no permitido)
def test_validar_destino_tipo_invalido(client):
    payload = {
        "tipo_destino": "impresora",  # No existe en la enumeración
        "nombre_destino": "IMP-PISO1",
    }
    response = client.post("/validar-destino", json=payload)
    # Pydantic devuelve 422 Unprocessable Entity
    assert response.status_code == 422


# 5. Test de error de Pydantic (Nombre demasiado corto)
def test_validar_destino_nombre_corto(client):
    payload = {
        "tipo_destino": "grupo",
        "nombre_destino": "ab",  # Menos de 3 caracteres
    }
    response = client.post("/validar-destino", json=payload)
    assert response.status_code == 422


# 6. Test de éxito para equipo con prefijo SRV-
def test_validar_destino_equipo_srv_exito(client):
    payload = {
        "tipo_destino": "equipo",
        "nombre_destino": "SRV-DC01",
    }
    response = client.post("/validar-destino", json=payload)
    assert response.status_code == 200
    assert response.json()["destino"] == "equipo:SRV-DC01"
