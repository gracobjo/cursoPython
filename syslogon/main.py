from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

from db import graba

app = FastAPI()


# Modelo de inicio de sesión

class Registro(BaseModel):
    inicio_sesion: datetime
    usuario: str
    pc: str
    gigas_libres: float # type: ignore
    ultimo_encendido: datetime
    

@app.post("/registra-inicio-sesion")
def registra(registro: Registro):
    graba(registro)
    return {"mensaje": "El registro se ha recibido"}

@app.get("/pcs-poco-espacio")   
def dame_pcs_poco_espacio():
    pcs_poco_espacio_libre=[]
    
    return pcs_poco_espacio_libre