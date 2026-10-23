# SCAD - Sistema Centralizado de Avisos de Dominio

Proyecto del curso **Introducción a la programación web con Python + FastAPI**.

## Arquitectura

- **Gestor de proyecto:** uv (Astral)
- **Backend:** FastAPI + SQLModel (ORM) + SQLite
- **Frontend:** HTML, CSS, JavaScript, HTMX con Jinja2 (Markdown → HTML en servidor)
- **Testing:** pytest con httpx / TestClient
- **Cliente Logon:** Script de inicio que invoca la API y lanza el navegador

## Estructura

```
scad/
├── profesor/     ← Implementación de referencia (demostraciones)
│   ├── src/
│   └── tests/
└── alumno/       ← Ejercicios resueltos
    ├── src/
    └── tests/
```

## Arranque

```powershell
# Instalar dependencias
uv sync

# Lanzar el servidor (profesor)
uv run uvicorn profesor.src.main:app --reload

# Lanzar el servidor (alumno)
uv run uvicorn alumno.src.main:app --reload

# Ejecutar tests
uv run pytest -v
```

## Endpoints principales

| Método | Ruta                     | Descripción                          | Auth  |
|--------|--------------------------|--------------------------------------|-------|
| GET    | `/`                      | Tablón de avisos (HTML + HTMX)        | No    |
| GET    | `/avisos`                | Listar avisos activos (JSON)          | No    |
| POST   | `/avisos`                | Crear aviso                           | Sí    |
| GET    | `/avisos/{id}`          | Obtener aviso por ID                  | No    |
| PATCH  | `/avisos/{id}`          | Actualizar aviso                      | Sí    |
| DELETE | `/avisos/{id}`          | Eliminar aviso                         | Sí    |
| POST   | `/api/v1/evaluar-avisos` | Evaluar avisos para un cliente        | No    |
| GET    | `/portal-avisos`        | Portal web de avisos (HTML)           | No    |

## Usuarios de administración (simulados)

| Usuario       | Contraseña      |
|---------------|-----------------|
| `admin_dom`   | `P@ssw0rd2026`  |
| `soporte_dom` | `AdminSCAD123`  |
