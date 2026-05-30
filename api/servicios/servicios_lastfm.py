import os
import requests
from dotenv import load_dotenv
import urllib3

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"

PAISES_MAP = {
    "México": "Mexico",
    "Mexico": "Mexico",
    "España": "Spain",
    "Espana": "Spain",
    "Estados Unidos": "United States",
    "Argentina": "Argentina",
    "Colombia": "Colombia",
    "Brasil": "Brazil",
    "Brazil": "Brazil"
}

DEFAULT_COUNTRIES = list(PAISES_MAP.keys())

CITY_OPTIONS = {
    "México": ["Ciudad de México", "Guadalajara", "Monterrey", "Veracruz", "Xalapa", "Puebla"],
    "España": ["Madrid", "Barcelona", "Valencia"],
    "Estados Unidos": ["Nueva York", "Los Ángeles", "Miami"],
    "Argentina": ["Buenos Aires", "Córdoba", "Rosario"],
    "Colombia": ["Bogotá", "Medellín", "Cali"],
    "Brasil": ["São Paulo", "Río de Janeiro", "Brasilia"]
}

CITY_FALLBACK = {
    "México": {
        "Ciudad de México": [
            {"nombre_cancion": "Amor Eterno", "nombre_artista": "Juan Gabriel", "reproducciones": 4200000},
            {"nombre_cancion": "Causa y Efecto", "nombre_artista": "Paulina Rubio", "reproducciones": 3100000},
            {"nombre_cancion": "La Bikina", "nombre_artista": "Luis Miguel", "reproducciones": 2900000},
            {"nombre_cancion": "Eres", "nombre_artista": "Café Tacvba", "reproducciones": 2700000},
            {"nombre_cancion": "Nada Valgo Sin Tu Amor", "nombre_artista": "Juanes", "reproducciones": 2500000}
        ],
        "Guadalajara": [
            {"nombre_cancion": "La Incondicional", "nombre_artista": "Luis Miguel", "reproducciones": 3300000},
            {"nombre_cancion": "De Música Ligera", "nombre_artista": "Soda Stereo", "reproducciones": 2800000},
            {"nombre_cancion": "Rayando el Sol", "nombre_artista": "Maná", "reproducciones": 2600000}
        ],
        "Veracruz": [
            {"nombre_cancion": "La Bamba", "nombre_artista": "Ritchie Valens", "reproducciones": 4800000},
            {"nombre_cancion": "La Cumbia del Sol", "nombre_artista": "Los Ángeles Azules", "reproducciones": 3900000},
            {"nombre_cancion": "La Boa", "nombre_artista": "La Sonora Santanera", "reproducciones": 3400000},
            {"nombre_cancion": "El Talismán", "nombre_artista": "Miguel Aceves Mejía", "reproducciones": 3000000}
        ],
        "Xalapa": [
            {"nombre_cancion": "La Pachanga", "nombre_artista": "José Luis Rodríguez", "reproducciones": 3500000},
            {"nombre_cancion": "El Listón de Tu Pelo", "nombre_artista": "Los Ángeles Azules", "reproducciones": 3200000},
            {"nombre_cancion": "No Me Queda Más", "nombre_artista": "Selena", "reproducciones": 3100000}
        ],
        "Puebla": [
            {"nombre_cancion": "Cielito Lindo", "nombre_artista": "Mariachi Vargas de Tecalitlán", "reproducciones": 5200000},
            {"nombre_cancion": "México Lindo y Querido", "nombre_artista": "Vicente Fernández", "reproducciones": 4500000},
            {"nombre_cancion": "Si Nos Dejan", "nombre_artista": "José Alfredo Jiménez", "reproducciones": 4100000}
        ]
    },
    "España": {
        "Madrid": [
            {"nombre_cancion": "Mediterráneo", "nombre_artista": "Joan Manuel Serrat", "reproducciones": 4500000}
        ]
    }
}


def obtener_top_global():
    try:
        response = requests.get(
            LASTFM_URL,
            params={
                "method": "chart.getTopTracks",
                "api_key": LASTFM_API_KEY,
                "format": "json",
                "limit": 10
            },
            verify=False,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        print("STATUS:", response.status_code)
        print("API KEY:", LASTFM_API_KEY)
        print("DATA LASTFM:", data)

        print("RESPUESTA LASTFM:")
        print(data)

        tracks = data.get("tracks", {}).get("track", [])

        if not tracks:
            return []

        top_global = []

        for i in tracks:
            top_global.append({
                "nombre_cancion": i.get("name", "Sin nombre"),
                "nombre_artista": i.get("artist", {}).get("name", "Desconocido"),
                "reproducciones": int(i.get("playcount", 0))
            })

        return top_global

    except Exception as e:
        print("ERROR EN obtener_top_global:", e)
        return []


def obtener_top_pais(pais):
    api_country = PAISES_MAP.get(pais)
    if not api_country:
        return []

    response = requests.get(
        LASTFM_URL,
        params={
            "method": "geo.getTopTracks",
            "country": api_country,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": 10
        },
        verify=False,
        timeout=15
    )

    response.raise_for_status()
    data = response.json()

    tracks = data.get("tracks", {}).get("track", [])

    if not isinstance(tracks, list):
        tracks = [tracks]

    top_pais = []

    for track in tracks:
        nombre_cancion = track.get("name", "N/D")

        artista = track.get("artist", {})

        if isinstance(artista, dict):
            nombre_artista = artista.get("name", "N/D")
        else:
            nombre_artista = str(artista)

        reproducciones = obtener_reproducciones_cancion(
            nombre_cancion,
            nombre_artista
        )

        top_pais.append({
            "pais": pais,
            "nombre_cancion": nombre_cancion,
            "nombre_artista": nombre_artista,
            "reproducciones": reproducciones
        })

    return top_pais

def obtener_paises_disponibles():
    return DEFAULT_COUNTRIES


def obtener_ciudades_por_pais(pais):
    return CITY_OPTIONS.get(pais, [])


def obtener_top_ciudad(pais, ciudad):
    if pais in CITY_FALLBACK and ciudad in CITY_FALLBACK[pais]:
        fallback_tracks = CITY_FALLBACK[pais][ciudad]
        if len(fallback_tracks) >= 10:
            return fallback_tracks[:10]

        top_country = obtener_top_pais(pais)
        extra_tracks = [track for track in top_country if track["nombre_cancion"] not in {t["nombre_cancion"] for t in fallback_tracks}]
        return (fallback_tracks + extra_tracks)[:10]

    # No city-level data from Last.fm; devolvemos el top del país como aproximación.
    tracks = obtener_top_pais(pais)
    return tracks[:10] if tracks else []


def obtener_top_paises_globales():
    top_paises = []

    for pais in DEFAULT_COUNTRIES:
        top_track = obtener_top_pais(pais)

        if top_track:
            top_paises.append(top_track[0])

    return top_paises

def obtener_artista_info(nombre_artista):
    response = requests.get(
        LASTFM_URL,
        params={
            "method": "artist.getInfo",
            "artist": nombre_artista,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        },
        timeout=15
    )

    response.raise_for_status()
    data = response.json()
    print(data)

    artista = data.get("artist", {})
    images = artista.get("image", [])
    imagen_url = ""
    if images:
        imagen_url = images[-1].get("#text", "")

    stats = artista.get("stats", {})
    
    return {
        "nombre": artista.get("name", ""),
        "imagen_url": imagen_url,
        "escuchas": int(stats.get("listeners", 0)),
        "reproducciones": int(stats.get("playcount", 0)),
        "tags": [tag.get("name", "") for tag in artista.get("tags", {}).get("tag", [])]
    }
    
def obtener_reproducciones_cancion(nombre_cancion, nombre_artista):
    response = requests.get(
        LASTFM_URL,
        params={
            "method": "track.getInfo",
            "track": nombre_cancion,
            "artist": nombre_artista,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        },
        verify=False,
        timeout=15
    )

    response.raise_for_status()
    data = response.json()

    track_info = data.get("track", {})

    raw_playcount = track_info.get("playcount") or 0

    try:
        return int(raw_playcount)
    except (ValueError, TypeError):
        return 0

    