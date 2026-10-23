(() => {
    const app = document.querySelector("#app");
    function createElement(tag, attributes = {}, textContent) {
        const element = document.createElement(tag);
        for (const [name, value] of Object.entries(attributes)) {
            element.setAttribute(name, value);
        }
        if (textContent !== undefined) element.textContent = textContent;
        return element;
    }

    const main = createElement("main", { class: "page" });
    const header = createElement("header", { class: "topbar" });
    header.appendChild(createElement("div", { class: "brand" }, "Agenda · API REST"));
    header.appendChild(createElement(
        "a",
        { class: "docs-link", href: "/docs" },
        "Documentación API ↗",
    ));
    main.appendChild(header);

    const hero = createElement("section", { class: "hero" });
    hero.appendChild(createElement("h1", {}, "Tu agenda de tareas"));
    hero.appendChild(createElement(
        "p",
        {},
        "Organiza tus pendientes y mantén tus fechas bajo control.",
    ));
    main.appendChild(hero);

    const layout = createElement("div", { class: "layout" });
    const agendaPanel = createElement("section", {
        class: "panel agenda",
        "aria-labelledby": "agenda-title",
    });
    const agendaHead = createElement("div", { class: "agenda-head" });
    agendaHead.appendChild(createElement("h2", { id: "agenda-title" }, "Próximas tareas"));
    const tabs = createElement("div", {
        class: "tabs",
        role: "tablist",
        "aria-label": "Filtrar agenda",
    });
    tabs.appendChild(createElement("button", {
        class: "tab",
        id: "pending-tab",
        role: "tab",
        "aria-selected": "true",
        "data-filter": "pending",
    }, "Pendientes"));
    tabs.appendChild(createElement("button", {
        class: "tab",
        id: "all-tab",
        role: "tab",
        "aria-selected": "false",
        "data-filter": "all",
    }, "Todas"));
    agendaHead.appendChild(tabs);
    agendaPanel.appendChild(agendaHead);
    agendaPanel.appendChild(createElement("div", {
        id: "agenda-content",
        "aria-live": "polite",
    }));
    layout.appendChild(agendaPanel);

    const summary = createElement("aside", {
        class: "summary",
        "aria-label": "Resumen de tareas",
    });
    summary.appendChild(createElement("h2", {}, "Resumen"));
    for (const [label, id] of [
        ["Pendientes", "pending-count"],
        ["Vencidas", "overdue-count"],
        ["Completadas", "completed-count"],
    ]) {
        const stat = createElement("div", { class: "stat" });
        stat.appendChild(createElement("span", {}, label));
        stat.appendChild(createElement("strong", { id }, "—"));
        summary.appendChild(stat);
    }
    summary.appendChild(createElement(
        "button",
        { class: "refresh", id: "refresh-button", type: "button" },
        "↻ Actualizar agenda",
    ));

    const createTaskForm = createElement("form", { class: "create", id: "create-form" });
    createTaskForm.appendChild(createElement("h3", {}, "Añadir una tarea"));
    const subjectField = createElement("div", { class: "field" });
    subjectField.appendChild(createElement("label", { for: "task-subject" }, "Asunto"));
    subjectField.appendChild(createElement("input", {
        id: "task-subject",
        name: "asunto",
        type: "text",
        maxlength: "200",
        placeholder: "¿Qué tienes que hacer?",
        required: "",
    }));
    createTaskForm.appendChild(subjectField);

    const dueField = createElement("div", { class: "field" });
    dueField.appendChild(createElement(
        "label",
        { for: "task-due" },
        "Fecha de vencimiento",
    ));
    dueField.appendChild(createElement("input", {
        id: "task-due",
        name: "fecha_vencimiento",
        type: "date",
        required: "",
    }));
    createTaskForm.appendChild(dueField);
    createTaskForm.appendChild(createElement(
        "button",
        { class: "submit", id: "submit-button", type: "submit" },
        "Crear tarea",
    ));
    createTaskForm.appendChild(createElement("p", {
        class: "form-error",
        id: "form-error",
        role: "alert",
        hidden: "",
    }));
    summary.appendChild(createTaskForm);
    layout.appendChild(summary);
    main.appendChild(layout);
    app.appendChild(main);

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
        agenda.replaceChildren(createElement("div", { class: "message" }, "Cargando agenda…"));
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
})();
