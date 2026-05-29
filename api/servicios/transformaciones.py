import logging
from database import obtener_conexion_bd

logger = logging.getLogger(__name__)

def limpiar_texto(texto):
    if not texto:
        return "desconocido"
    return texto.lower().strip()

def estandarizar_metricas_popularidad():
    conexion = obtener_conexion_bd()
    if not conexion:
        return {"status": "error", "mensaje": "No hay conexión a la BD"}

    try:
        cursor = conexion.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS popularidad_unificada (
                cancion_estandar VARCHAR(255),
                artista_estandar VARCHAR(255),
                cancion_original VARCHAR(255),
                artista_original VARCHAR(255),
                vistas_totales BIGINT DEFAULT 0,
                likes_totales BIGINT DEFAULT 0,
                score_popularidad FLOAT,
                PRIMARY KEY (cancion_estandar, artista_estandar)
            )
        """)
        
        cursor.execute("""
            SELECT id_plataforma, cancion, vistas, likes
            FROM streaming_consumo
        """)
        datos_crudos = cursor.fetchall()
        
        datos_unificados = {}

        for fila in datos_crudos:
            id_plat, cancion_raw, vistas_raw, likes_raw = fila
            
            vistas = vistas_raw if vistas_raw is not None else 0
            likes = likes_raw if likes_raw is not None else 0

            artista = "Desconocido"
            cancion = cancion_raw if cancion_raw else "Desconocida"
            
            if cancion_raw and "-" in cancion_raw:
                partes = cancion_raw.split("-", 1)
                artista = partes[0].strip()
                cancion = partes[1].strip()

            cancion_std = limpiar_texto(cancion)
            artista_std = limpiar_texto(artista)
            
            llave = (cancion_std, artista_std)
            
            if llave not in datos_unificados:
                datos_unificados[llave] = {
                    "cancion_original": cancion,
                    "artista_original": artista,
                    "vistas": 0,
                    "likes": 0
                }
            
            datos_unificados[llave]["vistas"] += vistas
            datos_unificados[llave]["likes"] += likes

        for llave, metricas in datos_unificados.items():
            cancion_std, artista_std = llave
            
            peso_vistas = 1.0
            peso_likes = 5.0
            score_calculado = (metricas["vistas"] * peso_vistas) + (metricas["likes"] * peso_likes)
            
            cursor.execute("""
                INSERT INTO popularidad_unificada 
                (cancion_estandar, artista_estandar, cancion_original, artista_original, vistas_totales, likes_totales, score_popularidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cancion_estandar, artista_estandar) 
                DO UPDATE SET 
                    vistas_totales = EXCLUDED.vistas_totales,
                    likes_totales = EXCLUDED.likes_totales,
                    score_popularidad = EXCLUDED.score_popularidad;
            """, (cancion_std, artista_std, metricas["cancion_original"], metricas["artista_original"], metricas["vistas"], metricas["likes"], score_calculado))

        conexion.commit()
        cursor.close()
        return {"status": "success", "mensaje": "Métricas de popularidad estandarizadas correctamente"}

    except Exception as e:
        logger.error(f"Error en transformación CU-05: {e}")
        conexion.rollback()
        return {"status": "error", "mensaje": str(e)}
    finally:
        conexion.close()