from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


class Bar(BaseModel):
    nombre: str
    puntuacion: float


class ActualizarPuntuacion(BaseModel):
    puntuacion: float


class BarConId(BaseModel):
    id: int
    nombre: str
    direccion: str
    barrio: str
    especialidad: str
    puntuacion: float


class CrearBar(BaseModel):
    nombre: str
    direccion: str
    barrio: str
    especialidad: str
    puntuacion: float


class BaresDeCiudad(BaseModel):
    ciudad: str
    bares: list[BarConId]


bares = {
    bar.nombre: bar
    for bar in (
        Bar(nombre="Bar A", puntuacion=4.5),
        Bar(nombre="Bar B", puntuacion=3.8),
        Bar(nombre="Bar C", puntuacion=4.2),
        Bar(nombre="Bar D", puntuacion=4.9),
        Bar(nombre="Bar E", puntuacion=3.5)
    )
}

ciudad = "Valladolid"
bares2 = {
    bar.id: bar
    for bar in (
        BarConId(
            id=1,
            nombre="Bar La Tasquita",
            direccion="Calle Paraíso, 4",
            barrio="Centro",
            especialidad="Tapas tradicionales",
            puntuacion=4.5,
        ),
        BarConId(
            id=2,
            nombre="El Corcho",
            direccion="Calle Correos, 2",
            barrio="Centro",
            especialidad="Pinchos de bacalao",
            puntuacion=4.7,
        ),
        BarConId(
            id=3,
            nombre="Bar Jero",
            direccion="Calle Correos, 11",
            barrio="Centro",
            especialidad="Tigres y croquetas",
            puntuacion=4.6,
        ),
        BarConId(
            id=4,
            nombre="La Criolla",
            direccion="Plaza Martí y Monsó, 3",
            barrio="Centro",
            especialidad="Pinchos creativos",
            puntuacion=4.4,
        ),
        BarConId(
            id=5,
            nombre="La Pícara",
            direccion="Calle Calixto Fernández de la Torre, 3",
            barrio="Centro",
            especialidad="Vinos y tapas",
            puntuacion=4.3,
        ),
        BarConId(
            id=6,
            nombre="El Penicilino",
            direccion="Calle Esgueva, 9",
            barrio="Universidad",
            especialidad="Ambiente universitario",
            puntuacion=4.2,
        ),
        BarConId(
            id=7,
            nombre="La Negra Flor",
            direccion="Calle San Ignacio, 11",
            barrio="La Rondilla",
            especialidad="Cervezas artesanas",
            puntuacion=4.1,
        ),
    )
}


@app.get("/lista_bares", response_model=list[Bar])
def devuelve_lista_bares() -> list[Bar]:
    return sorted(bares.values(), key=lambda bar: bar.puntuacion, reverse=True)


@app.get("/mejor_bar", response_model=Bar)
def devuelve_mejor_bar() -> Bar:
    return max(bares.values(), key=lambda bar: bar.puntuacion)


@app.patch("/bares/{nombre}/puntuacion", response_model=Bar)
def actualizar_puntuacion(nombre: str, actualizacion: ActualizarPuntuacion) -> Bar:
    bar = bares.get(nombre)
    if bar is None:
        raise HTTPException(status_code=404, detail="Bar no encontrado")

    bar.puntuacion = actualizacion.puntuacion
    return bar


@app.get("/bares2", response_model=BaresDeCiudad)
def listar_bares2() -> BaresDeCiudad:
    bares_ordenados = sorted(
        bares2.values(),
        key=lambda bar: bar.puntuacion,
        reverse=True,
    )
    return BaresDeCiudad(ciudad=ciudad, bares=bares_ordenados)


@app.get("/bares2/mejor", response_model=BarConId)
def obtener_mejor_bar2() -> BarConId:
    if not bares2:
        raise HTTPException(status_code=404, detail="No hay bares")

    return max(bares2.values(), key=lambda bar: bar.puntuacion)


@app.get("/bares2/{id_bar}", response_model=BarConId)
def obtener_bar2(id_bar: int) -> BarConId:
    bar = bares2.get(id_bar)
    if bar is None:
        raise HTTPException(status_code=404, detail="Bar no encontrado")

    return bar


@app.patch("/bares2/{id_bar}/puntuacion", response_model=BarConId)
def actualizar_puntuacion2(
    id_bar: int,
    actualizacion: ActualizarPuntuacion,
) -> BarConId:
    bar = bares2.get(id_bar)
    if bar is None:
        raise HTTPException(status_code=404, detail="Bar no encontrado")

    bar_actualizado = bar.model_copy(
        update={"puntuacion": actualizacion.puntuacion}
    )
    bares2[id_bar] = bar_actualizado
    return bar_actualizado


@app.post(
    "/bares2",
    response_model=BarConId,
    status_code=status.HTTP_201_CREATED,
)
def crear_bar2(nuevo_bar: CrearBar) -> BarConId:
    id_bar = max(bares2, default=0) + 1
    bar = BarConId(id=id_bar, **nuevo_bar.model_dump())
    bares2[id_bar] = bar
    return bar


@app.delete("/bares2/{id_bar}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bar2(id_bar: int) -> Response:
    if id_bar not in bares2:
        raise HTTPException(status_code=404, detail="Bar no encontrado")

    del bares2[id_bar]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
