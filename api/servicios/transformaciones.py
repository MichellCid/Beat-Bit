import logging
from database import obtener_conexion_bd

logger = logging.getLogger(__name__)

def limpiar_texto(texto):
    if not texto:
        return "desconocido"
    return texto.lower().strip()

def crear_esquema_data_warehouse():
    return {"status": "success", "mensaje": "Esquema centralizado en init.sql"}