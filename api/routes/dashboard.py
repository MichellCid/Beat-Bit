from servicios.servicios_spotify import busquedaArtista, obtenerTopCancionesArtista, obtenerAlbumPopular, obtener_generos_por_region
from fastapi import APIRouter, HTTPException
from servicios.servicios_lastfm import (
    obtener_top_global,
    obtener_top_pais,
    obtener_top_paises_globales,
    obtener_ciudades_por_pais,
    obtener_top_ciudad,
    obtener_paises_disponibles,
    obtener_artista_info,
    obtener_top_audiencia_regiones
)

router = APIRouter(prefix="/api")

@router.get("/top-audiencia-regiones")
def top_audiencia_regiones():
    return {
        "top_audiencia": obtener_top_audiencia_regiones()
    }

@router.get("/top-global")
def top_global():
    top_global_data = obtener_top_global()
    
    nombre_artista_top = top_global_data[0]["nombre_artista"] if top_global_data else "Sin datos disponibles"
    
    imagen_artista_top = ""
    if nombre_artista_top != "Sin datos disponibles":
        try:
            info_artista = obtener_artista_info(nombre_artista_top)
            imagen_artista_top = info_artista.get("imagen_url", "")
        except Exception as e:
            print(f"Error obteniendo imagen: {e}")

    return {
        "top_global": top_global_data,
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

@router.get("/historico")
def obtener_historico(inicio: int = None, fin: int = None):
    datos_completos = [
        {"anio": 2015, "pop": 85, "rock": 70, "reggaeton": 30, "hip_hop": 60},
        {"anio": 2016, "pop": 82, "rock": 68, "reggaeton": 40, "hip_hop": 65},
        {"anio": 2017, "pop": 80, "rock": 65, "reggaeton": 60, "hip_hop": 70},
        {"anio": 2018, "pop": 78, "rock": 60, "reggaeton": 75, "hip_hop": 75},
        {"anio": 2019, "pop": 75, "rock": 58, "reggaeton": 85, "hip_hop": 80},
        {"anio": 2020, "pop": 70, "rock": 55, "reggaeton": 90, "hip_hop": 82},
        {"anio": 2021, "pop": 68, "rock": 50, "reggaeton": 95, "hip_hop": 85},
        {"anio": 2022, "pop": 72, "rock": 48, "reggaeton": 92, "hip_hop": 88},
        {"anio": 2023, "pop": 75, "rock": 45, "reggaeton": 88, "hip_hop": 90},
        {"anio": 2024, "pop": 78, "rock": 42, "reggaeton": 85, "hip_hop": 95},
        {"anio": 2025, "pop": 80, "rock": 40, "reggaeton": 82, "hip_hop": 92},
        {"anio": 2026, "pop": 83, "rock": 38, "reggaeton": 80, "hip_hop": 90},
    ]

    if inicio and fin:
        datos_filtrados = [d for d in datos_completos if inicio <= d["anio"] <= fin]
    else:
        datos_filtrados = datos_completos

    return {"evolucion": datos_filtrados}

@router.get("/popularidad-genero-region")
def popularidad_genero_region(region: str, genero: str = None):
    try:
        generos = obtener_generos_por_region(region, genero)
        return {"generos": generos}
    except Exception as e:
        print(f"Error procesando popularidad_genero_region: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar los datos de Spotify.")

#-- ----------------------------------------------------------------------------------------------------------------------
#Endpoints para obtener datos de los artistas desde Spotify

@router.get("/artista/buscar/{nombre}")
def buscarArtista(nombre: str):
    artista = busquedaArtista(nombre)

    print("artista", artista)

    if not artista:
        return {
            "error": "Artista no encontrado"
        }

    return {
        #"nombre": artista.get("name"),
        #"seguidores": artista.get("followers", {}).get("total", 0),
        #"generos": artista.get("genres", []),
        #"imagen": artista.get("images", [{}])[0].get("url", "")
        "artista": artista
    }
