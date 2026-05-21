import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"

def obtener_top_global():
    api_key = os.getenv("LASTFM_API_KEY")

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

    top_global = []

    for i in data["tracks"]["track"]:
        top_global.append({
            "nombre_cancion": i["name"],
            "nombre_artista": i["artist"]["name"],
            "reproducciones": int(i["playcount"])
        })
    return top_global

def obtener_artista_info(nombre_artista):
    api_key = os.getenv("LASTFM_API_KEY")

    response = requests.get(LASTFM_URL, params={
        "method": "artist.getInfo",
        "artist": nombre_artista,
        "api_key": api_key,
        "format": "json"
    })

    response.raise_for_status()
    data = response.json()

    artista = data.get("artist", {})
    images = artista.get("image", [])
    imagen_url = "" 
    if images:
        imagen_url = images[-1].get("#text", "")

    return {
        "nombre": artista.get("name", ""),
        "imagen_url": imagen_url
    }

    