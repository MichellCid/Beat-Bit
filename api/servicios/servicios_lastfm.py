import os
import requests
import urllib3

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


def obtener_top_global():
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
    print(data)

    top_global = []

    for i in data["tracks"]["track"]:
        top_global.append({
            "nombre_cancion": i["name"],
            "nombre_artista": i["artist"]["name"],
            "reproducciones": int(i["playcount"])
        })
    return top_global


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

def obtener_top_paises_globales():
    top_paises = []

    for pais in DEFAULT_COUNTRIES:
        top_track = obtener_top_pais(pais)

        if top_track:
            top_paises.append(top_track[0])

    return top_paises

def obtener_artista_info(nombre_artista):
    response = requests.get(LASTFM_URL, params={
        "method": "artist.getInfo",
        "artist": nombre_artista,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    })

    response.raise_for_status()
    data = response.json()
    print(data)

    artista = data.get("artist", {})
    images = artista.get("image", [])
    imagen_url = ""
    if images:
        imagen_url = images[-1].get("#text", "")

    return {
        "nombre": artista.get("name", ""),
        "imagen_url": imagen_url
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

    