import json
import time
import sys
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from database import obtener_conexion_bd
from servicios.transformaciones import crear_esquema_data_warehouse, limpiar_texto
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

def procesar_evento(evento):
    conexion = obtener_conexion_bd()
    if not conexion: return
    try:
        cursor = conexion.cursor()
        cancion = limpiar_texto(evento["cancion"])
        artista = limpiar_texto(evento["artista"])
        pais = evento["pais"]
        vistas = evento["vistas"]
        likes = evento["likes"]
        fecha_dt = datetime.fromisoformat(evento["timestamp"])
        
        cursor.execute("INSERT INTO dim_cancion (nombre_cancion) VALUES (%s) ON CONFLICT (nombre_cancion) DO NOTHING", (cancion,))
        cursor.execute("INSERT INTO dim_artista (nombre_artista) VALUES (%s) ON CONFLICT (nombre_artista) DO NOTHING", (artista,))
        cursor.execute("INSERT INTO dim_geografia (pais, ciudad) VALUES (%s, %s) ON CONFLICT (pais, ciudad) DO NOTHING", (pais, 'Desconocida'))
        cursor.execute("INSERT INTO dim_tiempo (fecha, anio, mes, dia) VALUES (%s, %s, %s, %s) ON CONFLICT (fecha) DO NOTHING", 
                       (fecha_dt.date(), fecha_dt.year, fecha_dt.month, fecha_dt.day))
        
        cursor.execute("SELECT id_cancion FROM dim_cancion WHERE nombre_cancion = %s", (cancion,))
        id_cancion = cursor.fetchone()[0]
        cursor.execute("SELECT id_artista FROM dim_artista WHERE nombre_artista = %s", (artista,))
        id_artista = cursor.fetchone()[0]
        cursor.execute("SELECT id_geografia FROM dim_geografia WHERE pais = %s", (pais,))
        id_geografia = cursor.fetchone()[0]
        cursor.execute("SELECT id_tiempo FROM dim_tiempo WHERE fecha = %s", (fecha_dt.date(),))
        id_tiempo = cursor.fetchone()[0]
        
        score = (vistas * 1.0) + (likes * 5.0)
        cursor.execute("""
            INSERT INTO hechos_consumo (id_cancion, id_artista, id_tiempo, id_geografia, vistas, likes, score_popularidad)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_cancion, id_artista, id_tiempo, id_geografia, vistas, likes, score))
        conexion.commit()
        cursor.close()
        print(f"Exito en DB: {cancion} - {artista} (Score: {score})")
    except Exception as e:
        print(f"ERROR: {e}")
        conexion.rollback()
    finally:
        conexion.close()

def iniciar_consumidor():
    crear_esquema_data_warehouse()
    intentos = 0
    while intentos < 10:
        try:
            consumidor = KafkaConsumer('eventos_reproduccion', bootstrap_servers=['kafka:9092'],
                                     value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                                     auto_offset_reset='earliest')
            print("Consumidor escuchando eventos...")
            for mensaje in consumidor:
                procesar_evento(mensaje.value)
            break
        except Exception:
            intentos += 1
            time.sleep(5)

if __name__ == "__main__":
    time.sleep(15)
    iniciar_consumidor()