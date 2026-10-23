from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel


app = FastAPI()


@app.get("/")
def raiz():
    return {"mensaje": "Hola mundo"}


@app.get("/lista-alumnos")
def devuelve_lista_alumnos():
    alumnos = ["Ana", "Lucía", "María"]
    return alumnos


@app.middleware("http")
async def capture_raw_request(request: Request, call_next):
    # 1. Leer el cuerpo de la solicitud en bytes
    body = await request.body()
    
    # 2. Obtener la versión de HTTP (por defecto 1.1)
    http_version = request.scope.get("http_version", "1.1")
    
    # 3. Reconstruir las cabeceras en formato texto plano
    headers_list = [f"{key}: {value}" for key, value in request.headers.items()]
    headers_str = "\r\n".join(headers_list)
    
    # 4. Unir todo simulando el formato HTTP en bruto
    raw_request = (
        f"{request.method} {request.url.path} HTTP/{http_version}\r\n"
        f"{headers_str}\r\n\r\n"
        f"{body.decode('utf-8', errors='ignore')}"
    )
    
    # Mostrar por pantalla (consola)
    print("\n--- CONTENIDO EN BRUTO DE LA SOLICITUD ---")
    print(raw_request)
    print("-------------------------------------------\n")
    
    response = await call_next(request)
    return response

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/sumaLista")
async def suma_valores(valores: list[int] = Query(...)):
    return {"suma": sum(valores)}

@app.get("/multiplicacionLista")
async def multiplicacion_valores(valores: list[int] = Query(...)):
    resultado = 1
    for valor in valores:
        resultado *= valor
    return {"multiplicacion": resultado}

@app.get("/division")
async def division(dividendo: float, divisor: float):
    if divisor == 0:
        raise HTTPException(status_code=400, detail="No se puede dividir entre cero")
    return {"division": dividendo / divisor}

articulos = [
    {"id": 1, "nombre": "Artículo 1", "precio": 10.0},
    {"id": 2, "nombre": "Artículo 2", "precio": 20.0},
    {"id": 3, "nombre": "Artículo 3", "precio": 30.0},
    {"id": 4, "nombre": "Artículo 4", "precio": 40.0},
    {"id": 5, "nombre": "Artículo 5", "precio": 50.0},
    {"id": 6, "nombre": "Artículo 6", "precio": 60.0},
    {"id": 7, "nombre": "Artículo 7", "precio": 70.0},
    {"id": 8, "nombre": "Artículo 8", "precio": 80.0},
    {"id": 9, "nombre": "Artículo 9", "precio": 90.0},
    {"id": 10, "nombre": "Artículo 10", "precio": 100.0}]


@app.get("/articulos/")
async def read_articulo(desde: int = 0, limite: int = 10):
    return articulos[desde:desde + limite]

alumnos = [
    {"id": 1, "nombre": "Ana", "edad": 20},
    {"id": 2, "nombre": "Lucía", "edad": 22},
    {"id": 3, "nombre": "María", "edad": 21},
    {"id": 4, "nombre": "Juan", "edad": 23},
    {"id": 5, "nombre": "Pedro", "edad": 24},
    {"id": 6, "nombre": "Luis", "edad": 25},
    {"id": 7, "nombre": "Marta", "edad": 26},
    {"id": 8, "nombre": "Sofía", "edad": 27},
    {"id": 9, "nombre": "Carlos", "edad": 28},
    {"id": 10, "nombre": "Laura", "edad": 29}]

@app.get("/alumnos/")
async def read_alumnos(desde: int = 0, limite: int = 10):
    return alumnos[desde:desde + limite]

@app.get("/alumnosId/{alumno_id}")
async def read_alumno(alumno_id: int):
    alumno = next((alumno for alumno in alumnos if alumno["id"] == alumno_id), None)
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

"""@app.get("/alumno")
async def dame_alumno(alumno_id: int):
    u_id, u_nombre, u_edad = alumnos[alumno_id]
    """

class Persona(BaseModel):
    id: int
    nombre: str
    edad: int
    telefono: str | None = None  # Campo opcional con valor por defecto None

@app.post("/persona/")
async def nueva_persona(persona: Persona):
    return {"mensaje": "Persona creada", "persona": persona}


class Item(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None  # Campo opcional 
    precio: float
    tax: float | None = None  # Campo opcional

@app.post("/items/")
async def create_item(item: Item):
    tax_value = item.tax if item.tax else 0
    precio_con_impuesto = item.precio + tax_value
    return {f"mensaje": f"Item creado: {item.nombre}", "item": item, "precio_con_impuesto": precio_con_impuesto}    


