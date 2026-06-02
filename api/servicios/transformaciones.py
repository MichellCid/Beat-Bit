import logging
import random
from database import obtener_conexion_bd
import os
import pandas as pd

DATASETS_RUTA = os.getenv("DATASETS_RUTA", "datasets")

logger = logging.getLogger(__name__)

def limpiar_texto(texto):
    if not texto:
        return "desconocido"
    return texto.lower().strip()

def crear_esquema_data_warehouse():
    return {"status": "success", "mensaje": "Esquema centralizado en init.sql"}



#----------------------------------------------------------------------------------------------
#historico de artistas populares por años por las canciones populares

def limpiar_numero(valor):
    try:
        return int(str(valor).replace("'", "").replace("'", "").strip())
    except Exception:
        return 0
    

def obtener_columna(row, columnas, posibles):
    for nombre in posibles:
        if nombre in columnas:
            return row[columnas[nombre]]
    return None


def generar_fecha_random ():
    return random.randint(1920, 2026)


def generar_popularidad_random ():
    return random.randint(40, 100)

def obtener_anio(fecha):
    try:
        texto_fecha = str(fecha).strip()
        return int(texto_fecha[:4])
    except Exception:
        return generar_fecha_random()


def leer_csv_seguro(path):
    codificaciones = ["utf-8", "latin1", "ISO-8859-1", "cp1252"]

    for codificacion in codificaciones:
        try:
            return pd.read_csv(path, encoding=codificacion)
        except UnicodeDecodeError:
            continue

    return pd.read_csv(path, encoding="latin1", errors="replace")
    

def transformar_datos(path):
    df = leer_csv_seguro(path)
    columnas = {c.lower().strip(): c for c in df.columns}
    registros = []

    for _, row in df.iterrows():
        nombre_cancion = obtener_columna(row, columnas, ["track_name", "name"])
        artista = obtener_columna(row, columnas, ["artist_name", "artists", "artist(s)_name"])

        if not nombre_cancion or not artista:
            continue

        #artista = str(artista).split(",")[0].strip()
        artista = (str(artista).replace("[", "").replace("]", "").replace("'", "").replace('"', "").split(";")[0].split(",")[0].strip())
        nombre_cancion = str(nombre_cancion).strip()

        artista = artista[:255]
        nombre_cancion = nombre_cancion[:255]

        anio_lanzamiento = obtener_columna(row, columnas, ["release_date", "released_year"])

        anio_lanzamiento = obtener_anio(anio_lanzamiento)

        try:
            anio_lanzamiento = int(anio_lanzamiento)
        except Exception:
            anio_lanzamiento = generar_fecha_random()

        
        anio_popularidad = anio_lanzamiento

        popularidad = obtener_columna(row, columnas, ["popularity"])

        try:
            popularidad = float(popularidad)
        except Exception:
            popularidad = generar_popularidad_random()

        streams = obtener_columna(row, columnas, ["streams"])
        if streams is not None:
            reproducciones = limpiar_numero(streams)
        else:
            reproducciones = int(popularidad * 1000000)

        if reproducciones <= 0:
            reproducciones = int(popularidad * 1000000)

        
        registros.append({
            "nombre_cancion": nombre_cancion,
            "nombre_artista": artista,
            "anio_lanzamiento": anio_lanzamiento,
            "anio_popularidad": anio_popularidad,
            "reproducciones": reproducciones,
            "popularidad": popularidad,
        })

    return registros


def cargar_datos(registros):
    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    try:
        for registro in registros:
            cursor.execute("""
                insert into dim_artista (nombre) values (%s) on conflict (nombre) do nothing
                            """, (registro["nombre_artista"],))
            
            cursor.execute(""" 
                select id_artista from dim_artista where nombre = %s;
            """, (registro["nombre_artista"],))

            id_artista = cursor.fetchone()[0]

            cursor.execute("""
                insert into dim_cancion(nombre_cancion, anio_lanzamiento) values (%s, %s) on conflict (nombre_cancion) do update set anio_lanzamiento = excluded.anio_lanzamiento returning id_cancion;
            """, (registro["nombre_cancion"], registro["anio_lanzamiento"]))

            id_cancion = cursor.fetchone()[0]

            fecha = f"{registro['anio_popularidad']}-01-01"

            cursor.execute("""
                insert into dim_tiempo(fecha, anio, mes, dia, nombre_mes) values (%s, %s, %s, %s, %s) on conflict (fecha) do update set fecha = excluded.fecha returning id_tiempo;
            """, (fecha, registro["anio_popularidad"], 1, 1, "Enero"))

            id_tiempo = cursor.fetchone()[0]

            cursor.execute("""
                insert into fact_popularidad_cancion(id_cancion, id_artista, id_tiempo, reproducciones, popularidad) values (%s, %s, %s, %s, %s) on conflict (id_cancion, id_artista, id_tiempo) do update set reproducciones = excluded.reproducciones, popularidad = excluded.popularidad;
            """, (id_cancion, id_artista, id_tiempo, registro["reproducciones"], registro["popularidad"]))

            conexion.commit()

    except Exception as e:
        conexion.rollback()
        raise e

    finally:
        cursor.close()
        conexion.close()


def pipeline_etl_popularidad():
    archivos = [
        "spotify_tracks.csv",
        "spotify_1921_2020.csv",
        "spotify_2023.csv"
    ]

    todos = []

    for archivo in archivos:
        path = os.path.join(DATASETS_RUTA, archivo)

        if not os.path.exists(path):
            continue

        registros = transformar_datos(path)
        todos.extend(registros)

    cargar_datos(todos)

    return{
        "mensaje": "ejecutando pipeline etl de popularidad",
        "total_registros": len(todos)
    }

def consultar_top_artistas_por_anio(inicio, fin, limite=3):
    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    
    cursor.execute(""" 
        with ranking as (
                select dt.anio, da.nombre as nombre_artista, sum(fp.reproducciones) as total_reproducciones,
                   row_number() over (partition by dt.anio order by sum(fp.reproducciones) desc) as posicion
                from fact_popularidad_cancion fp
                join dim_artista da on fp.id_artista = da.id_artista
                join dim_tiempo dt on fp.id_tiempo = dt.id_tiempo
                where dt.anio between %s and %s
                group by dt.anio, da.nombre)
        select anio, nombre_artista, total_reproducciones from ranking where posicion <= %s order by anio asc, total_reproducciones desc;
                
                    
                   
    """, (inicio, fin, limite))

    filas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return [
        {
            "anio": fila[0],
            "artista": fila[1],
            "reproducciones": fila[2]
        }
        for fila in filas
    ]



