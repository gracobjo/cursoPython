"""
Configuración del sistema de logging para SCAD.

Persiste los eventos de auditoría en un archivo .log y también
los muestra en consola durante el desarrollo.
"""

import logging
from pathlib import Path

# Crear el directorio de logs si no existe dentro de profesor/src/
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "scad.log"

# Configurar el Logger del sistema
logger = logging.getLogger("scad_auditoria")
logger.setLevel(logging.INFO)

# Formateador de texto estructurado para el archivo de logs
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Manejador para guardar en fichero de texto
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

# Manejador adicional para mostrar también en consola durante el desarrollo
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Evitar duplicar manejadores si el módulo se importa varias veces
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
