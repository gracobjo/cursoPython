from datetime import date, datetime, timedelta, timezone
from itertools import count
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.params import Query
from pydantic import AliasChoices, BaseModel, Field, computed_field, field_validator
from fastapi.responses import HTMLResponse
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
def raiz() -> HTMLResponse:
    return HTMLResponse(
        """
        <!doctype html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="theme-color" content="#f4f6fb">
            <title>Agenda de tareas</title>
            <style>
                :root {
                    color-scheme: light;
                    font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
                    color: #172033;
                    background: #f4f6fb;
                }
                * { box-sizing: border-box; }
                body {
                    margin: 0;
                    background:
                        linear-gradient(180deg, rgba(11, 20, 38, .28), #f4f6fb 390px),
                        url("/static/welcome.png") center top / auto 360px no-repeat,
                        #f4f6fb;
                }
                a { color: inherit; }
                .page { width: min(1080px, calc(100% - 36px)); margin: auto; padding: 38px 0 64px; }
                .topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; color: white; }
                .brand { font-size: .86rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
                .docs-link {
                    padding: 10px 14px;
                    border: 1px solid rgba(255,255,255,.55);
                    border-radius: 10px;
                    color: white;
                    font-size: .9rem;
                    font-weight: 700;
                    text-decoration: none;
                    background: rgba(15,23,42,.25);
                }
                .hero { padding: 47px 0 32px; color: white; }
                .hero h1 { margin: 0; font-size: clamp(2.2rem, 6vw, 3.5rem); letter-spacing: -.045em; }
                .hero p { margin: 10px 0 0; color: #e2e8f0; font-size: 1.05rem; }
                .layout { display: grid; grid-template-columns: minmax(0, 1fr) 310px; align-items: start; gap: 22px; }
                .panel, .summary {
                    border: 1px solid #e5e9f2;
                    border-radius: 18px;
                    background: rgba(255,255,255,.96);
                    box-shadow: 0 14px 38px rgba(23,32,51,.08);
                }
                .agenda { padding: 24px; }
                .agenda-head { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 20px; }
                .agenda-head h2, .summary h2 { margin: 0; font-size: 1.25rem; letter-spacing: -.02em; }
                .tabs { display: inline-flex; gap: 4px; padding: 4px; border-radius: 11px; background: #f1f4f9; }
                .tab {
                    border: 0; border-radius: 8px; padding: 9px 12px; color: #667085;
                    font: inherit; font-size: .88rem; font-weight: 700; cursor: pointer; background: transparent;
                }
                .tab[aria-selected="true"] { color: #1d4ed8; background: white; box-shadow: 0 1px 4px #18243a1c; }
                .date-group { margin-top: 25px; }
                .date-title { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; margin: 0 0 10px; }
                .date-title h3 { margin: 0; font-size: .94rem; font-weight: 800; text-transform: capitalize; }
                .date-title span { color: #8992a3; font-size: .8rem; }
                .task-list { display: grid; gap: 9px; }
                .task {
                    display: grid; grid-template-columns: 22px minmax(0,1fr) auto; align-items: center; gap: 12px;
                    padding: 14px; border: 1px solid #e9edf4; border-radius: 13px; background: #fff;
                }
                .task input { width: 18px; height: 18px; margin: 0; accent-color: #2563eb; cursor: pointer; }
                .task-title { margin: 0; font-size: .96rem; font-weight: 750; overflow-wrap: anywhere; }
                .task-meta { display: flex; flex-wrap: wrap; gap: 8px 12px; margin-top: 5px; color: #7a8495; font-size: .79rem; }
                .badge { padding: 6px 9px; border-radius: 999px; white-space: nowrap; font-size: .75rem; font-weight: 800; }
                .badge.soon { color: #9a6700; background: #fff3cd; }
                .badge.later { color: #276749; background: #e5f6ed; }
                .badge.overdue { color: #b42318; background: #feeceb; }
                .task.done .task-title { color: #8992a3; text-decoration: line-through; }
                .empty, .message { padding: 34px 16px; text-align: center; color: #778195; }
                .message.error { color: #b42318; }
                .summary { padding: 21px; }
                .summary h2 { margin-bottom: 16px; }
                .stat { display: flex; justify-content: space-between; align-items: baseline; padding: 13px 0; border-top: 1px solid #edf0f5; }
                .stat span { color: #707b8d; font-size: .9rem; }
                .stat strong { font-size: 1.4rem; }
                .create { margin-top: 18px; padding-top: 18px; border-top: 1px solid #edf0f5; }
                .create h3 { margin: 0 0 13px; font-size: 1rem; }
                label { display: block; margin: 0 0 6px; color: #596579; font-size: .8rem; font-weight: 700; }
                .field { margin-bottom: 12px; }
                input[type="text"], input[type="date"] {
                    width: 100%; min-height: 42px; padding: 9px 11px; border: 1px solid #dce2ec;
                    border-radius: 9px; color: #172033; font: inherit; background: white;
                }
                .submit {
                    width: 100%; min-height: 43px; border: 0; border-radius: 10px; color: white;
                    font: inherit; font-weight: 750; cursor: pointer; background: #2563eb;
                }
                .submit:hover { background: #1d4ed8; }
                .submit:disabled { cursor: wait; opacity: .65; }
                .form-error { margin: 10px 0 0; color: #b42318; font-size: .84rem; }
                .refresh { border: 0; padding: 7px 0; color: #2563eb; font: inherit; font-size: .84rem; font-weight: 750; cursor: pointer; background: transparent; }
                @media (max-width: 760px) {
                    .page { width: min(100% - 24px, 600px); padding-top: 20px; }
                    .hero { padding: 54px 0 24px; }
                    .layout { grid-template-columns: 1fr; }
                    .summary { grid-row: 1; }
                    .agenda { padding: 18px 14px; }
                    .agenda-head { align-items: flex-start; flex-direction: column; }
                    .task { grid-template-columns: 22px minmax(0,1fr); }
                    .task .badge { grid-column: 2; justify-self: start; }
                    body { background-size: auto 310px; }
                }
                @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; } }
            </style>
        </head>
        <body>
            <main class="page">
                <header class="topbar">
                    <div class="brand">Agenda · API REST</div>
                    <a class="docs-link" href="/docs">Documentación API ↗</a>
                </header>
                <section class="hero">
                    <h1>Tu agenda de tareas</h1>
                    <p>Organiza tus pendientes y mantén tus fechas bajo control.</p>
                </section>
                <div class="layout">
                    <section class="panel agenda" aria-labelledby="agenda-title">
                        <div class="agenda-head">
                            <h2 id="agenda-title">Próximas tareas</h2>
                            <div class="tabs" role="tablist" aria-label="Filtrar agenda">
                                <button class="tab" id="pending-tab" role="tab" aria-selected="true" data-filter="pending">Pendientes</button>
                                <button class="tab" id="all-tab" role="tab" aria-selected="false" data-filter="all">Todas</button>
                            </div>
                        </div>
                        <div id="agenda-content" aria-live="polite"><div class="message">Cargando agenda…</div></div>
                    </section>
                    <aside class="summary" aria-label="Resumen de tareas">
                        <h2>Resumen</h2>
                        <div class="stat"><span>Pendientes</span><strong id="pending-count">—</strong></div>
                        <div class="stat"><span>Vencidas</span><strong id="overdue-count">—</strong></div>
                        <div class="stat"><span>Completadas</span><strong id="completed-count">—</strong></div>
                        <button class="refresh" id="refresh-button" type="button">↻ Actualizar agenda</button>
                        <form class="create" id="create-form">
                            <h3>Añadir una tarea</h3>
                            <div class="field">
                                <label for="task-subject">Asunto</label>
                                <input id="task-subject" name="asunto" type="text" maxlength="200" placeholder="¿Qué tienes que hacer?" required>
                            </div>
                            <div class="field">
                                <label for="task-due">Fecha de vencimiento</label>
                                <input id="task-due" name="fecha_vencimiento" type="date" required>
                            </div>
                            <button class="submit" id="submit-button" type="submit">Crear tarea</button>
                            <p class="form-error" id="form-error" role="alert" hidden></p>
                        </form>
                    </aside>
                </div>
            </main>
            <script>
                const agenda = document.querySelector("#agenda-content");
                const pendingCount = document.querySelector("#pending-count");
                const overdueCount = document.querySelector("#overdue-count");
                const completedCount = document.querySelector("#completed-count");
                const form = document.querySelector("#create-form");
                const formError = document.querySelector("#form-error");
                let currentFilter = "pending";
                let allTasks = [];
                let pendingTasks = [];

                function localDate(isoDate) {
                    const [year, month, day] = isoDate.split("-").map(Number);
                    return new Date(year, month - 1, day);
                }

                function formatDate(isoDate, options) {
                    return new Intl.DateTimeFormat("es-ES", options).format(localDate(isoDate));
                }

                function dateGroupLabel(isoDate) {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const due = localDate(isoDate);
                    const delta = Math.round((due - today) / 86400000);
                    if (delta === 0) return "Hoy";
                    if (delta === 1) return "Mañana";
                    if (delta === -1) return "Ayer";
                    return formatDate(isoDate, { weekday: "long", day: "numeric", month: "long" });
                }

                async function request(path, options = {}) {
                    const response = await fetch(path, {
                        ...options,
                        headers: { "Content-Type": "application/json", ...options.headers },
                    });
                    if (!response.ok) {
                        let detail = `Error ${response.status}`;
                        try {
                            const body = await response.json();
                            if (typeof body.detail === "string") detail = body.detail;
                        } catch {}
                        throw new Error(detail);
                    }
                    return response.status === 204 ? null : response.json();
                }

                function taskCard(task) {
                    const card = document.createElement("article");
                    card.className = `task${task.completed ? " done" : ""}`;
                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.checked = task.completed;
                    checkbox.setAttribute("aria-label", `${task.completed ? "Reabrir" : "Completar"}: ${task.asunto}`);
                    checkbox.addEventListener("change", () => toggleTask(task, checkbox));

                    const text = document.createElement("div");
                    const title = document.createElement("p");
                    title.className = "task-title";
                    title.textContent = task.asunto;
                    const meta = document.createElement("div");
                    meta.className = "task-meta";
                    const created = document.createElement("span");
                    created.textContent = `Creada el ${formatDate(task.fecha_creacion.slice(0, 10), { day: "numeric", month: "short", year: "numeric" })}`;
                    const due = document.createElement("span");
                    due.textContent = `Vence ${formatDate(task.fecha_vencimiento, { day: "numeric", month: "short", year: "numeric" })}`;
                    meta.append(created, due);
                    text.append(title, meta);

                    const badge = document.createElement("span");
                    const days = task.dias_restantes;
                    badge.className = `badge ${days < 0 ? "overdue" : days <= 2 ? "soon" : "later"}`;
                    badge.textContent = task.completed ? "Completada" :
                        days < 0 ? `Vencida hace ${Math.abs(days)} d` :
                        days === 0 ? "Vence hoy" :
                        days === 1 ? "Queda 1 día" : `Quedan ${days} días`;
                    card.append(checkbox, text, badge);
                    return card;
                }

                function renderTasks() {
                    const tasks = currentFilter === "pending" ? pendingTasks : allTasks;
                    agenda.replaceChildren();
                    if (!tasks.length) {
                        const empty = document.createElement("div");
                        empty.className = "empty";
                        empty.textContent = currentFilter === "pending"
                            ? "¡Todo al día! No tienes tareas pendientes."
                            : "Todavía no hay tareas en tu agenda.";
                        agenda.append(empty);
                        return;
                    }

                    const groups = new Map();
                    [...tasks].sort((a, b) => a.fecha_vencimiento.localeCompare(b.fecha_vencimiento) || a.id - b.id)
                        .forEach(task => {
                            if (!groups.has(task.fecha_vencimiento)) groups.set(task.fecha_vencimiento, []);
                            groups.get(task.fecha_vencimiento).push(task);
                        });
                    for (const [dueDate, items] of groups) {
                        const group = document.createElement("section");
                        group.className = "date-group";
                        const heading = document.createElement("div");
                        heading.className = "date-title";
                        const title = document.createElement("h3");
                        title.textContent = dateGroupLabel(dueDate);
                        const count = document.createElement("span");
                        count.textContent = `${items.length} ${items.length === 1 ? "tarea" : "tareas"}`;
                        heading.append(title, count);
                        const list = document.createElement("div");
                        list.className = "task-list";
                        items.forEach(task => list.append(taskCard(task)));
                        group.append(heading, list);
                        agenda.append(group);
                    }
                }

                async function loadTasks() {
                    agenda.innerHTML = '<div class="message">Cargando agenda…</div>';
                    try {
                        [allTasks, pendingTasks] = await Promise.all([
                            request("/TODO"),
                            request("/TODO/pendientes"),
                        ]);
                        const overdue = pendingTasks.filter(task => task.dias_restantes < 0).length;
                        pendingCount.textContent = pendingTasks.length;
                        overdueCount.textContent = overdue;
                        completedCount.textContent = allTasks.length - pendingTasks.length;
                        renderTasks();
                    } catch (error) {
                        agenda.replaceChildren();
                        const message = document.createElement("div");
                        message.className = "message error";
                        message.textContent = `No se pudo cargar la agenda: ${error.message}`;
                        agenda.append(message);
                    }
                }

                async function toggleTask(task, checkbox) {
                    checkbox.disabled = true;
                    try {
                        await request(`/TODO/${task.id}`, {
                            method: "PUT",
                            body: JSON.stringify({
                                asunto: task.asunto,
                                fecha_vencimiento: task.fecha_vencimiento,
                                completed: checkbox.checked,
                            }),
                        });
                        await loadTasks();
                    } catch (error) {
                        checkbox.checked = task.completed;
                        checkbox.disabled = false;
                        window.alert(`No se pudo actualizar la tarea: ${error.message}`);
                    }
                }

                document.querySelectorAll(".tab").forEach(tab => {
                    tab.addEventListener("click", () => {
                        currentFilter = tab.dataset.filter;
                        document.querySelectorAll(".tab").forEach(button =>
                            button.setAttribute("aria-selected", String(button === tab)));
                        renderTasks();
                    });
                });
                document.querySelector("#refresh-button").addEventListener("click", loadTasks);
                form.addEventListener("submit", async event => {
                    event.preventDefault();
                    formError.hidden = true;
                    const button = document.querySelector("#submit-button");
                    button.disabled = true;
                    try {
                        const values = new FormData(form);
                        await request("/TODO", {
                            method: "POST",
                            body: JSON.stringify({
                                asunto: values.get("asunto"),
                                fecha_vencimiento: values.get("fecha_vencimiento"),
                            }),
                        });
                        form.reset();
                        currentFilter = "pending";
                        document.querySelectorAll(".tab").forEach(tab =>
                            tab.setAttribute("aria-selected", String(tab.dataset.filter === "pending")));
                        await loadTasks();
                    } catch (error) {
                        formError.textContent = `No se pudo crear la tarea: ${error.message}`;
                        formError.hidden = false;
                    } finally {
                        button.disabled = false;
                    }
                });

                document.querySelector("#task-due").value = new Date().toLocaleDateString("en-CA");
                loadTasks();
            </script>
        </body>
        </html>
        """
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