from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from routes.dashboard import router as dashboard_router
from servicios.sincronizacion import sincronizar_datos
from servicios.servicios_spotify import busquedaArtista, obtenerTopCancionesArtista
from servicios.servicios_lastfm import obtener_artista_info
from servicios.servicios_youtube import buscar_metricas_youtube
from servicios.calculos import calcular_popularidad

from db.conexion import conexion


def tarea_sincronizacion_automatica():
    print("Ejecutando sincronización automática en segundo plano...")
    sincronizar_datos()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(tarea_sincronizacion_automatica, 'interval', minutes=1) 
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Beat & Bit API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
                   ],
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
    resultado = sincronizar_datos()
    return resultado

@app.get("/test-db")
def test_db():
    conexiondb = conexion()
    cursor = conexiondb.cursor()

    cursor.execute("SELECT COUNT(*) FROM dim_region;")
    total = cursor.fetchone()[0]

    cursor.close()
    conexiondb.close()

    return {
        "mensaje": "Conexión correcta con PostgreSQL",
        "regiones": total
    }


@app.get("/artista/{nombre}")
def obtener_artista(nombre: str):
    spotify = busquedaArtista(nombre)

    if not spotify:
        return {"error": "Artista no encontrado"}

    try:
        lastfm = obtener_artista_info(nombre)
    except Exception as e:
        print("ERROR LASTFM:", e)

        lastfm = {
            "escuchas": 0,
            "reproducciones": 0,
            "tags": []
        }

    try:
        youtube = buscar_metricas_youtube(nombre)
    except Exception as e:
        print("ERROR YOUTUBE:", e)

        youtube = {
            "vistas": 0,
            "likes": 0,
            "regiones": []
        }
    #lastfm = obtener_artista_info(nombre)
    #youtube = buscar_metricas_youtube(nombre)

    escuchas = lastfm.get("escuchas", 0)
    reproducciones = lastfm.get("reproducciones", 0)
    vistas = youtube.get("vistas", 0)
    likes = youtube.get("likes", 0)

    popularidad = calcular_popularidad(
        escuchas,
        reproducciones,
        vistas,
        likes
    )

    return {
        "artista": {
            "spotify_id": spotify.get("id"),
            "nombre": spotify.get("nombre"),
            "imagen": spotify.get("imagen"),
            "generos": spotify.get("generos", [])
        },
        "metricas": {
            "escuchas": escuchas,
            "reproducciones": reproducciones,
            "vistas": vistas,
            "likes": likes,
            "popularidad": popularidad
        },
        "regiones": youtube.get("regiones", [])
    }