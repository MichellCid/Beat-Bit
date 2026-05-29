import logging
from database import obtener_conexion_bd

logger = logging.getLogger(__name__)

def limpiar_texto(texto):
    if not texto:
        return "desconocido"
    return texto.lower().strip()

def crear_esquema_data_warehouse():
    conexion = obtener_conexion_bd()
    if not conexion:
        return {"status": "error", "mensaje": "No hay conexión a la BD"}

    try:
        cursor = conexion.cursor()
        
        cursor.execute("CREATE TABLE IF NOT EXISTS dim_artista (id_artista SERIAL PRIMARY KEY, nombre_artista VARCHAR(255) UNIQUE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS dim_cancion (id_cancion SERIAL PRIMARY KEY, nombre_cancion VARCHAR(255) UNIQUE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS dim_tiempo (id_tiempo SERIAL PRIMARY KEY, fecha DATE UNIQUE, anio INT, mes INT, dia INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS dim_geografia (id_geografia SERIAL PRIMARY KEY, pais VARCHAR(100), ciudad VARCHAR(100), UNIQUE(pais, ciudad))")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hechos_consumo (
                id_hecho SERIAL PRIMARY KEY,
                id_cancion INT REFERENCES dim_cancion(id_cancion),
                id_artista INT REFERENCES dim_artista(id_artista),
                id_tiempo INT REFERENCES dim_tiempo(id_tiempo),
                id_geografia INT REFERENCES dim_geografia(id_geografia),
                vistas BIGINT DEFAULT 0,
                likes BIGINT DEFAULT 0,
                score_popularidad FLOAT
            )
        """)
        
        conexion.commit()
        cursor.close()
        return {"status": "success", "mensaje": "Esquema creado correctamente"}

    except Exception as e:
        logger.error(f"Error creando esquema: {e}")
        conexion.rollback()
        return {"status": "error", "mensaje": str(e)}
    finally:
        conexion.close()