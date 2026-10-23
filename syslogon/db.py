from datetime import datetime
from pathlib import Path


NOMBRE_FICHERO_LOGS = Path(__file__).parent / "logs" / "logs.txt"
UMBRAL_ESPACIO_GB = 20.0


def graba(registro):
    NOMBRE_FICHERO_LOGS.parent.mkdir(parents=True, exist_ok=True)
    with open(NOMBRE_FICHERO_LOGS, "a", encoding="utf-8") as fichero:
        linea = (
            f"{registro.inicio_sesion} - Usuario: {registro.usuario}, "
            f"PC: {registro.pc}, Gigas libres: {registro.gigas_libres}, "
            f"Último encendido: {registro.ultimo_encendido}\n"
        )
        fichero.write(linea)
    return None


def _parsea_linea(linea: str) -> tuple[datetime, str, str, float, datetime]:
    try:
        inicio_sesion, datos = linea.rstrip("\n").split(" - Usuario: ", 1)
        usuario, datos = datos.split(", PC: ", 1)
        pc, datos = datos.split(", Gigas libres: ", 1)
        gigas_libres, ultimo_encendido = datos.split(", Último encendido: ", 1)
        return (
            datetime.fromisoformat(inicio_sesion),
            usuario.strip('"'),
            pc.strip('"'),
            float(gigas_libres),
            datetime.fromisoformat(ultimo_encendido),
        )
    except (IndexError, ValueError) as error:
        raise ValueError(f"Línea de registro no válida: {linea.rstrip()}") from error


def ordenadora(linea: str) -> str:
    return _parsea_linea(linea)[2]


def agrupadora(linea: str) -> str:
    return _parsea_linea(linea)[2]


def dame_pcs_poco_espacio_libre() -> list[str]:
    registros_recientes: dict[str, tuple[datetime, float]] = {}
    with open(NOMBRE_FICHERO_LOGS, "r", encoding="utf-8") as fichero:
        for linea in fichero:
            if not linea.strip():
                continue
            inicio_sesion, _, pc, gigas_libres, _ = _parsea_linea(linea)
            registro_actual = registros_recientes.get(pc)
            if registro_actual is None or inicio_sesion >= registro_actual[0]:
                registros_recientes[pc] = (inicio_sesion, gigas_libres)

    return sorted(
        pc
        for pc, (_, gigas_libres) in registros_recientes.items()
        if gigas_libres < UMBRAL_ESPACIO_GB
    )

if __name__ == "__main__":
    print(dame_pcs_poco_espacio_libre())

        