import json
import time
import sys
from kafka import KafkaConsumer
from database import obtener_conexion_bd
from servicios.transformaciones import limpiar_texto
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

MAPA_PAISES = {
    "Mexico": "MX",
    "Estados Unidos": "US",
    "Espana": "ES",
    "Colombia": "CO"
}

def procesar_evento(evento):
    conexion = obtener_conexion_bd()
    if not conexion: 
        return
        
    try:
        cursor = conexion.cursor()
        cancion = limpiar_texto(evento["cancion"])
        artista = limpiar_texto(evento["artista"])
        nombre_pais = evento["pais"]
        pais_codigo = MAPA_PAISES.get(nombre_pais, "GL")
        
        vistas = evento["vistas"]
        likes = evento["likes"]
        fecha_dt = datetime.fromisoformat(evento["timestamp"])
        
        cursor.execute("INSERT INTO dim_artista (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING", (artista,))
        cursor.execute("SELECT id_artista FROM dim_artista WHERE nombre = %s", (artista,))
        id_artista_res = cursor.fetchone()
        id_artista = id_artista_res[0] if id_artista_res else None

        cursor.execute("INSERT INTO dim_cancion (nombre_cancion) VALUES (%s) ON CONFLICT (nombre_cancion) DO NOTHING", (cancion,))
        cursor.execute("SELECT id_cancion FROM dim_cancion WHERE nombre_cancion = %s", (cancion,))
        id_cancion_res = cursor.fetchone()
        id_cancion = id_cancion_res[0] if id_cancion_res else None
        
        cursor.execute("INSERT INTO dim_region (codigo, nombre) VALUES (%s, %s) ON CONFLICT (codigo) DO NOTHING", (pais_codigo, nombre_pais))
        cursor.execute("SELECT id_region FROM dim_region WHERE codigo = %s", (pais_codigo,))
        id_region_res = cursor.fetchone()
        id_region = id_region_res[0] if id_region_res else None
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        nombre_mes = meses[fecha_dt.month - 1]
        cursor.execute("INSERT INTO dim_tiempo (fecha, anio, mes, dia, nombre_mes) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (fecha) DO NOTHING", 
                       (fecha_dt.date(), fecha_dt.year, fecha_dt.month, fecha_dt.day, nombre_mes))
        cursor.execute("SELECT id_tiempo FROM dim_tiempo WHERE fecha = %s", (fecha_dt.date(),))
        id_tiempo_res = cursor.fetchone()
        id_tiempo = id_tiempo_res[0] if id_tiempo_res else None
        
        score = (vistas * 1.0) + (likes * 5.0)
        
        if id_cancion and id_artista and id_tiempo and id_region:
            cursor.execute("""
                INSERT INTO fact_rendimiento_streaming (id_cancion, id_artista, id_tiempo, id_region, vistas, likes, score_popularidad, tipo_ingesta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'REALTIME_KAFKA')
                ON CONFLICT (id_artista, id_tiempo, id_region, id_cancion, tipo_ingesta)
                DO UPDATE SET vistas = fact_rendimiento_streaming.vistas + EXCLUDED.vistas, 
                              likes = fact_rendimiento_streaming.likes + EXCLUDED.likes,
                              score_popularidad = fact_rendimiento_streaming.score_popularidad + EXCLUDED.score_popularidad
            """, (id_cancion, id_artista, id_tiempo, id_region, vistas, likes, score))
        
        conexion.commit()
        cursor.close()
        
    except Exception:
        conexion.rollback()
    finally:
        conexion.close()

def iniciar_consumidor():
    intentos = 0
    while intentos < 20:
        try:
            consumidor = KafkaConsumer(
                'eventos_reproduccion',
                bootstrap_servers=['kafka:9092'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='music_dwh_group'
            )
            for mensaje in consumidor:
                procesar_evento(mensaje.value)
            break
        except Exception:
            intentos += 1
            time.sleep(10)

if __name__ == "__main__":
    time.sleep(5)
    iniciar_consumidor()