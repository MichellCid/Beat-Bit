from fastapi import APIRouter
from servicios.servicios_lastfm import obtener_top_global, obtener_artista_info

router = APIRouter()

@router.get("/top-global")
def top_global():
    top_global = obtener_top_global()
    
    nombre_artista_top = top_global[0]["nombre_artista"] if top_global else "Sin datos disponibles"
    info_artista_top = obtener_artista_info(nombre_artista_top)

    return {
        "top_global": top_global,
        "artista_top": {
            "nombre": nombre_artista_top,
            "imagen": info_artista_top.get("imagen_url")
        }
    }