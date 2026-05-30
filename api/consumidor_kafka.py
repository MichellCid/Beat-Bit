import json
import time
import sys
from kafka import KafkaConsumer
from database import obtener_conexion_bd
from servicios.transformaciones import limpiar_texto
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

# Mapeo para evitar que "Estados Unidos" rompa el VARCHAR(10) de dim_region
MAPA_PAISES = {
    "Mexico": "MX",
    "Estados Unidos": "US",
    "Espana": "ES",
    "Colombia": "CO"
}

def procesar_evento(evento):
    conexion = obtener_conexion_bd()
    if not conexion: 
        print("ERROR: No se pudo obtener la conexión a la BD PostgreSQL.")
        return
        
    try:
        cursor = conexion.cursor()
        cancion = limpiar_texto(evento["cancion"])
        artista = limpiar_texto(evento["artista"])
        nombre_pais = evento["pais"]
        pais_codigo = MAPA_PAISES.get(nombre_pais, "DESC")
        
        vistas = evento["vistas"]
        likes = evento["likes"]
        fecha_dt = datetime.fromisoformat(evento["timestamp"])
        
        # 1. Dimensión Artista
        cursor.execute("INSERT INTO dim_artista (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING", (artista,))
        cursor.execute("SELECT id_artista FROM dim_artista WHERE nombre = %s", (artista,))
        id_artista_res = cursor.fetchone()
        id_artista = id_artista_res[0] if id_artista_res else None

        # 2. Dimensión Canción
        if id_artista:
            cursor.execute("INSERT INTO dim_cancion (nombre_cancion, id_artista) VALUES (%s, %s) ON CONFLICT (nombre_cancion) DO NOTHING", (cancion, id_artista))
        cursor.execute("SELECT id_cancion FROM dim_cancion WHERE nombre_cancion = %s", (cancion,))
        id_cancion_res = cursor.fetchone()
        id_cancion = id_cancion_res[0] if id_cancion_res else None
        
        # 3. Dimensión Región (Usando el código corto)
        cursor.execute("INSERT INTO dim_region (codigo, nombre) VALUES (%s, %s) ON CONFLICT (codigo) DO NOTHING", (pais_codigo, nombre_pais))
        cursor.execute("SELECT id_region FROM dim_region WHERE codigo = %s", (pais_codigo,))
        id_region_res = cursor.fetchone()
        id_region = id_region_res[0] if id_region_res else None
        
        # 4. Dimensión Tiempo
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        nombre_mes = meses[fecha_dt.month - 1]
        cursor.execute("INSERT INTO dim_tiempo (fecha, anio, mes, dia, nombre_mes) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (fecha) DO NOTHING", 
                       (fecha_dt.date(), fecha_dt.year, fecha_dt.month, fecha_dt.day, nombre_mes))
        cursor.execute("SELECT id_tiempo FROM dim_tiempo WHERE fecha = %s", (fecha_dt.date(),))
        id_tiempo_res = cursor.fetchone()
        id_tiempo = id_tiempo_res[0] if id_tiempo_res else None
        
        # 5. Tabla de Hechos
        score = (vistas * 1.0) + (likes * 5.0)
        
        if id_cancion and id_artista and id_tiempo and id_region:
            cursor.execute("""
                INSERT INTO hechos_consumo (id_cancion, id_artista, id_tiempo, id_region, vistas, likes, score_popularidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_cancion, id_artista, id_tiempo, id_region, vistas, likes, score))

        
        conexion.commit()
        cursor.close()
        print(f"Éxito guardando: {cancion} - {artista} (País: {pais_codigo}, Score: {score})")
        
    except Exception as e:
        print(f"ERROR procesando evento: {e}")
        conexion.rollback()
    finally:
        conexion.close()

def iniciar_consumidor():
    intentos = 0
    while intentos < 10:
        try:
            print(f"Intentando conectar a Kafka... (Intento {intentos + 1})")
            consumidor = KafkaConsumer(
                'eventos_reproduccion',
                bootstrap_servers=['kafka:9092'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='music_dwh_group'
            )
            print("¡Conectado! Consumidor escuchando eventos exitosamente...")
            for mensaje in consumidor:
                procesar_evento(mensaje.value)
            break
        except Exception as e:
            print(f"Fallo temporal con Kafka: {e}")
            intentos += 1
            time.sleep(5)

if __name__ == "__main__":
    print("Iniciando contenedor del consumidor. Esperando 5 segundos...")
    time.sleep(5)
    iniciar_consumidor()