from fastapi import APIRouter
from servicios.servicios_lastfm import (
    obtener_top_global,
    obtener_top_pais,
    obtener_top_paises_globales,
    obtener_ciudades_por_pais,
    obtener_top_ciudad,
    obtener_paises_disponibles
)

router = APIRouter()

@router.get("/top-global")
def top_global():
    top_global = obtener_top_global()
    
    nombre_artista_top = top_global[0]["nombre_artista"] if top_global else "Sin datos disponibles"
    imagen_artista_top = top_global[0].get("imagen_artista") if top_global else ""

    return {
        "top_global": top_global,
        "artista_top": {
            "nombre": nombre_artista_top,
            "imagen": imagen_artista_top
        }
    }

@router.get("/paises")
def paises():
    return {
        "paises": obtener_paises_disponibles()
    }

@router.get("/top-paises")
def top_paises(country: str = None):
    if country:
        return {
            "top_paises": obtener_top_pais(country),
            "country": country
        }

    return {
        "top_paises": obtener_top_paises_globales()
    }

@router.get("/ciudades")
def ciudades(country: str):
    return {
        "country": country,
        "ciudades": obtener_ciudades_por_pais(country)
    }

@router.get("/top-ciudad")
def top_ciudad(country: str, city: str):
    return {
        "country": country,
        "city": city,
        "top_ciudad": obtener_top_ciudad(country, city)
    }