import os
import requests
import logging
from datetime import date
from db.conexion import conexion
from database import obtener_conexion_bd

logger = logging.getLogger(__name__)

def extraer_datos_youtube():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return [
            {"id_plataforma": "YT_001", "cancion": "Blinding Lights", "vistas": 5000000, "likes": 80000},
            {"id_plataforma": "YT_001", "cancion": "Blinding Lights", "vistas": 5000000, "likes": 80000}, 
            {"id_plataforma": "YT_002", "cancion": "Shape of You", "vistas": 4500000, "likes": 75000}
        ]

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "videoCategoryId": "10", 
        "key": api_key,
        "maxResults": 15
    }
    response = requests.get(url, params=params)
    if response.status_code in [401, 403]:
        raise Exception(f"Token expirado o rechazado. HTTP: {response.status_code}")
        
    response.raise_for_status()
    data = response.json()
    
    resultados = []
    for item in data.get("items", []):
        resultados.append({
            "id_plataforma": f"YT_{item['id']}",
            "cancion": item["snippet"]["title"],
            "vistas": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0))
        })
    return resultados

def sincronizar_datos():
    conexion = obtener_conexion_bd()
    if not conexion:
        return {"status": "error", "mensaje": "No hay conexión a la BD"}

    exito_parcial = False
    datos_crudos = []

    try:
        datos_yt = extraer_datos_youtube()
        datos_crudos.extend(datos_yt)
    except Exception:
        exito_parcial = True 

    datos_limpios = {}
    for item in datos_crudos:
        if item["id_plataforma"] not in datos_limpios:
            datos_limpios[item["id_plataforma"]] = item

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS streaming_consumo (
                id_plataforma VARCHAR(50) PRIMARY KEY,
                cancion VARCHAR(255),
                vistas BIGINT,
                likes BIGINT
            )
        """)
        for dato in datos_limpios.values():
            cursor.execute("""
                INSERT INTO streaming_consumo (id_plataforma, cancion, vistas, likes)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id_plataforma) 
                DO UPDATE SET vistas = EXCLUDED.vistas, likes = EXCLUDED.likes;
            """, (dato["id_plataforma"], dato["cancion"], dato["vistas"], dato["likes"]))
        
        conexion.commit()
        cursor.close()
    except Exception:
        conexion.rollback()
        return {"status": "error", "mensaje": "Error de base de datos"}
    finally:
        conexion.close()

    if exito_parcial:
        return {"status": "warning", "mensaje": "Error: Sincronización parcial"}
    return {"status": "success", "mensaje": "Sincronización exitosa"}

def guardar_datos_artista(artista, metricas, regiones):
    conn = conexion()
    cursor = conn.cursor()
    try:
        hoy = date.today()
        cursor.execute("""
            INSERT INTO dim_artista (nombre, imagen, spotify_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (nombre)
            DO UPDATE SET
                imagen = EXCLUDED.imagen,
                spotify_id = EXCLUDED.spotify_id
            RETURNING id_artista;
        """, (artista["nombre"], artista["imagen"], artista["spotify_id"]))
        id_artista = cursor.fetchone()[0]

        if artista.get("generos"):
            for genero in artista["generos"]:
                cursor.execute("""
                    INSERT INTO dim_genero (nombre)
                    VALUES (%s)
                    ON CONFLICT (nombre) DO NOTHING
                    RETURNING id_genero;
                """, (genero,))
                resultado_genero = cursor.fetchone()
                
                if resultado_genero:
                    id_genero = resultado_genero[0]
                else:
                    cursor.execute("SELECT id_genero FROM dim_genero WHERE nombre = %s;", (genero,))
                    id_genero = cursor.fetchone()[0]
                    
                cursor.execute("""
                    INSERT INTO bridge_artista_genero (id_artista, id_genero)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (id_artista, id_genero))

        cursor.execute("""
            INSERT INTO dim_tiempo (fecha, anio, mes, dia, nombre_mes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (fecha)
            DO UPDATE SET fecha = EXCLUDED.fecha
            RETURNING id_tiempo;
        """, (hoy, hoy.year, hoy.month, hoy.day, hoy.strftime("%B")))
        id_tiempo = cursor.fetchone()[0]

        cursor.execute("SELECT id_region FROM dim_region WHERE codigo = 'GL';")
        id_region_global = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO fact_rendimiento_streaming (
                id_artista, id_tiempo, id_region, id_cancion, escuchas, reproducciones,
                vistas, likes, score_popularidad, tipo_ingesta
            )
            VALUES (%s, %s, %s, NULL, %s, %s, %s, %s, %s, 'BATCH_API')
            ON CONFLICT (id_artista, id_tiempo, id_region, id_cancion, tipo_ingesta)
            DO UPDATE SET
                escuchas = EXCLUDED.escuchas,
                reproducciones = EXCLUDED.reproducciones,
                vistas = EXCLUDED.vistas,
                likes = EXCLUDED.likes,
                score_popularidad = EXCLUDED.score_popularidad,
                fecha_registro = CURRENT_TIMESTAMP;
        """, (
            id_artista, id_tiempo, id_region_global,
            metricas["escuchas"], metricas["reproducciones"],
            metricas["vistas"], metricas["likes"], metricas["popularidad"]
        ))

        for region in regiones:
            cursor.execute("SELECT id_region FROM dim_region WHERE codigo = %s;", (region["codigo"],))
            resultado_region = cursor.fetchone()
            if not resultado_region:
                continue
            id_region = resultado_region[0]
            
            cursor.execute("""
                INSERT INTO fact_rendimiento_streaming (
                    id_artista, id_region, id_tiempo, id_cancion,
                    vistas, likes, score_popularidad, tipo_ingesta
                )
                VALUES (%s, %s, %s, NULL, %s, %s, %s, 'BATCH_API')
                ON CONFLICT (id_artista, id_tiempo, id_region, id_cancion, tipo_ingesta)
                DO UPDATE SET
                    vistas = EXCLUDED.vistas,
                    likes = EXCLUDED.likes,
                    score_popularidad = EXCLUDED.score_popularidad,
                    fecha_registro = CURRENT_TIMESTAMP;
            """, (
                id_artista, id_region, id_tiempo,
                region["vistas"], region["likes"], region["popularidad_region"]
            ))

        conn.commit()
        return id_artista

    except Exception:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def obtener_metricas_anteriores_por_nombre(nombre):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.vistas, f.likes
        FROM fact_rendimiento_streaming f
        JOIN dim_artista da ON f.id_artista = da.id_artista
        JOIN dim_region dr ON f.id_region = dr.id_region
        WHERE da.nombre = %s AND dr.codigo = 'GL' AND f.tipo_ingesta = 'BATCH_API'
        ORDER BY f.fecha_registro DESC
        LIMIT 1;
    """, (nombre,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()

    if not fila:
        return {"vistas": 0, "likes": 0}
    return {"vistas": fila[0], "likes": fila[1]}

def obtener_artistas_guardados():
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id_artista, nombre FROM dim_artista;")
    artistas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id_artista": fila[0], "nombre": fila[1]} for fila in artistas]

def obtener_datos_artista_hoy(nombre):
    return None