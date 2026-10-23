from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()

templates = Jinja2Templates(directory="plantillas")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # return {"titulo": "Curso", "texto": "Hola a todos"}
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"titulo": "Curso", "texto": "Hola a todos"}
    )