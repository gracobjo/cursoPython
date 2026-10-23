from datetime import date, datetime, timedelta, timezone
from itertools import count
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.params import Query
from pydantic import AliasChoices, BaseModel, Field, computed_field, field_validator
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
todos: dict[int, "Todo"] = {}
todo_ids = count(11)

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)

@app.get("/")
def raiz():
    return {"message": {"message": "Bienvenido a la API de FastAPI!"}}


@app.get("/app", response_class=FileResponse)
def agenda() -> FileResponse:
    return FileResponse(
        Path(__file__).parent / "templates" / "agenda.html",
        media_type="text/html",
    )

class TodoInput(BaseModel):
    asunto: str = Field(
        min_length=1,
        validation_alias=AliasChoices("asunto", "title"),
    )
    fecha_vencimiento: date = Field(
        validation_alias=AliasChoices("fecha_vencimiento", "due_date"),
    )

    @field_validator("asunto")
    @classmethod
    def validate_asunto(cls, value: str) -> str:
        asunto = value.strip()
        if not asunto:
            raise ValueError("El asunto no puede estar vacío")
        return asunto


class TodoCreate(TodoInput):
    pass


class TodoUpdate(TodoInput):
    completed: bool


class Todo(TodoInput):
    id: int
    completed: bool = False
    fecha_creacion: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    @computed_field
    @property
    def dias_restantes(self) -> int:
        return (self.fecha_vencimiento - datetime.now(timezone.utc).date()).days

    @computed_field
    @property
    def title(self) -> str:
        return self.asunto


_tareas_de_ejemplo = [
    ("Revisar correos", 1),
    ("Preparar reunión de equipo", 2),
    ("Actualizar documentación", 3),
    ("Enviar propuesta al cliente", 4),
    ("Revisar presupuesto", 5),
    ("Organizar archivos del proyecto", 6),
    ("Preparar presentación", 7),
    ("Responder consultas pendientes", 8),
    ("Planificar la próxima semana", 9),
    ("Hacer copia de seguridad", 10),
]
todos.update(
    {
        todo_id: Todo(
            id=todo_id,
            asunto=asunto,
            fecha_vencimiento=date.today() + timedelta(days=dias),
        )
        for todo_id, (asunto, dias) in enumerate(_tareas_de_ejemplo, start=1)
    }
)


@app.post("/TODO", response_model=Todo, status_code=status.HTTP_201_CREATED)
def crear_todo(todo: TodoCreate):
    nuevo_todo = Todo(
        id=next(todo_ids),
        asunto=todo.asunto,
        fecha_vencimiento=todo.fecha_vencimiento,
    )
    todos[nuevo_todo.id] = nuevo_todo
    return nuevo_todo


@app.get("/TODO", response_model=list[Todo])
def listar_todos():
    return list(todos.values())


@app.get(
    "/TODO/pendientes",
    response_model=list[Todo],
    summary="Listar TODO pendientes",
    description=(
        "Devuelve las tareas que todavía no están completadas. "
        "Ejemplo: `GET /TODO/pendientes`"
    ),
)
def listar_todos_pendientes():
    return [todo for todo in todos.values() if not todo.completed]


@app.get("/TODO/{todo_id}", response_model=Todo)
def obtener_todo(todo_id: int):
    todo = todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return todo


@app.put("/TODO/{todo_id}", response_model=Todo)
def actualizar_todo(todo_id: int, cambios: TodoUpdate):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    todo_actualizado = Todo(
        id=todo_id,
        asunto=cambios.asunto,
        fecha_vencimiento=cambios.fecha_vencimiento,
        completed=cambios.completed,
        fecha_creacion=todos[todo_id].fecha_creacion,
    )
    todos[todo_id] = todo_actualizado
    return todo_actualizado


@app.delete("/TODO/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_todo(todo_id: int):
    if todos.pop(todo_id, None) is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")