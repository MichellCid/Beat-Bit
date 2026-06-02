from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.dashboard import router as dashboard_router
from servicios.sincronizacion import sincronizar_datos, guardar_datos_artista, obtener_metricas_anteriores_por_nombre, obtener_datos_artista_hoy, obtener_artistas_guardados
from servicios.servicios_spotify import busquedaArtista, obtenerTopCancionesArtista, obtenerAlbumPopular, obtenerCancionMasPopular
from servicios.servicios_lastfm import obtener_artista_info
from servicios.servicios_youtube import buscar_metricas_youtube
from servicios.calculos import calcular_popularidad
from servicios.transformaciones import crear_esquema_data_warehouse
from apscheduler.schedulers.background import BackgroundScheduler
from db.conexion import conexion

def actualizar_metricas_artistas_guardados():
    artistas = obtener_artistas_guardados()
    for artista_bd in artistas:
        nombre = artista_bd["nombre"]
        spotify = busquedaArtista(nombre)
        if not spotify:
            continue
        try:
            lastfm = obtener_artista_info(nombre)
        except Exception:
            lastfm = {"escuchas": 0, "reproducciones": 0, "tags": []}
        try:
            youtube = buscar_metricas_youtube(nombre)
        except Exception:
            youtube = {"vistas": 0, "likes": 0, "regiones": []}

        escuchas = lastfm.get("escuchas", 0)
        reproducciones = lastfm.get("reproducciones", 0)
        vistas = youtube.get("vistas", 0)
        likes = youtube.get("likes", 0)
        popularidad = calcular_popularidad(escuchas, reproducciones, vistas, likes)

        artista_response = {
            "spotify_id": spotify.get("id"),
            "nombre": spotify.get("nombre"),
            "imagen": spotify.get("imagen"),
            "generos": spotify.get("generos", [])
        }
        metricas_response = {
            "escuchas": escuchas,
            "reproducciones": reproducciones,
            "vistas": vistas,
            "likes": likes,
            "popularidad": popularidad
        }
        regiones_response = youtube.get("regiones", [])

        guardar_datos_artista(artista_response, metricas_response, regiones_response)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        actualizar_metricas_artistas_guardados,
        "cron",
        hour=5,
        minute=59
    )
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Beat & Bit API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)

@app.get("/")
def home():
    return {"message": "API funcionando"}

@app.post("/api/sincronizar")
def endpoint_sincronizar():
    resultado_extraccion = sincronizar_datos()
    resultado_transformacion = crear_esquema_data_warehouse()
    
    return {
        "status": resultado_extraccion.get("status", "error"),
        "mensaje": resultado_extraccion.get("mensaje", "Sincronización terminada"),
        "extraccion": resultado_extraccion,
        "transformacion": resultado_transformacion
    }

@app.get("/test-db")
def test_db():
    conexiondb = conexion()
    cursor = conexiondb.cursor()
    cursor.execute("SELECT COUNT(*) FROM dim_region;")
    total = cursor.fetchone()[0]
    cursor.close()
    conexiondb.close()
    return {"mensaje": "Conexión correcta con PostgreSQL", "regiones": total}

@app.get("/artista/{nombre}")
def obtener_artista(nombre: str):
    spotify = busquedaArtista(nombre)
    
    if not spotify:
        return {"error": "Artista no encontrado"}
    
    top_canciones = obtenerTopCancionesArtista(nombre)
    cancion_mas_famosa = obtenerCancionMasPopular(top_canciones)
    album_mas_famoso = obtenerAlbumPopular(top_canciones)

    try:
        lastfm = obtener_artista_info(nombre)
    except Exception:
        lastfm = {"escuchas": 0, "reproducciones": 0, "tags": []}

    try:
        youtube = buscar_metricas_youtube(nombre)
    except Exception:
        youtube = {"vistas": 0, "likes": 0, "regiones": []}

    escuchas = lastfm.get("escuchas", 0)
    reproducciones = lastfm.get("reproducciones", 0)
    vistas = youtube.get("vistas", 0)
    likes = youtube.get("likes", 0)

    popularidad = calcular_popularidad(escuchas, reproducciones, vistas, likes)

    artista_response = {
        "spotify_id": spotify.get("id"),
        "nombre": spotify.get("nombre"),
        "imagen": spotify.get("imagen"),
        "generos": spotify.get("generos", [])
    }

    metricas_response = {
        "escuchas": escuchas,
        "reproducciones": reproducciones,
        "vistas": vistas,
        "likes": likes,
        "popularidad": popularidad,
    }

    regiones_response = youtube.get("regiones", [])

    id_artista = guardar_datos_artista(artista_response, metricas_response, regiones_response)

    return {
        "id_artista": id_artista,
        "artista": artista_response,
        "metricas": metricas_response,
        "cancion_mas_famosa": cancion_mas_famosa,
        "album_mas_famoso": album_mas_famoso,
        "top_10_canciones": top_canciones,
        "regiones": regiones_response
    }

@app.get("/artista/{id_artista}/historico")
def historico_artista(id_artista: int):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dt.fecha, f.escuchas, f.reproducciones, f.vistas, f.likes, f.score_popularidad
        FROM fact_rendimiento_streaming f
        JOIN dim_tiempo dt ON f.id_tiempo = dt.id_tiempo
        JOIN dim_region dr ON f.id_region = dr.id_region
        WHERE f.id_artista = %s AND dr.codigo = 'GL' AND f.tipo_ingesta = 'BATCH_API'
        ORDER BY dt.fecha;
    """, (id_artista,))
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    historico = []
    for fila in filas:
        historico.append({
            "fecha": str(fila[0]),
            "escuchas": fila[1],
            "reproducciones": fila[2],
            "vistas": fila[3],
            "likes": fila[4],
            "popularidad": float(fila[5])
        })
    return {"historico": historico}

@app.get("/artista/{id_artista}/regiones")
def regiones_artista(id_artista: int):
    conn = conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dr.codigo, dr.nombre, f.vistas, f.likes, f.score_popularidad
        FROM fact_rendimiento_streaming f
        JOIN dim_region dr ON f.id_region = dr.id_region
        WHERE f.id_artista = %s AND dr.codigo != 'GL' AND f.tipo_ingesta = 'BATCH_API'
        ORDER BY f.score_popularidad DESC;
    """, (id_artista,))
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    regiones = []
    for fila in filas:
        regiones.append({
            "codigo": fila[0],
            "region": fila[1],
            "vistas": fila[2],
            "likes": fila[3],
            "popularidad_region": float(fila[4])
        })
    return {
        "recomendacion_gira": regiones[:3],
        "regiones": regiones
    }