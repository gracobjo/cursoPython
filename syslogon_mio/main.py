from fastapi import FastAPI

app = FastAPI()

@app.get("/registro_inicio_sesion")
async def registro_inicio_sesion():
    return {"message": "Registro de inicio de sesión exitoso"}