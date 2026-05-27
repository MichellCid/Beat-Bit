import os
import base64
import time
import requests
from requests.exceptions import HTTPError

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_TOKEN_CACHE = {"token": None, "expires_at": 0}

COUNTRY_CODE_MAP = {
    "México": "MX",
    "España": "ES",
    "Estados Unidos": "US",
    "Argentina": "AR",
    "Colombia": "CO",
    "Brasil": "BR"
}

CITY_OPTIONS = {
    "México": ["Ciudad de México", "Guadalajara", "Monterrey"],
    "España": ["Madrid", "Barcelona", "Valencia"],
    "Estados Unidos": ["Nueva York", "Los Ángeles", "Miami"],
    "Argentina": ["Buenos Aires", "Córdoba", "Rosario"],
    "Colombia": ["Bogotá", "Medellín", "Cali"],
    "Brasil": ["São Paulo", "Río de Janeiro", "Brasilia"]
}

SPOTIFY_SEARCH_MARKET = "US"


def _spotify_get_access_token():
    now = time.time()
    if SPOTIFY_TOKEN_CACHE["token"] and now < SPOTIFY_TOKEN_CACHE["expires_at"] - 60:
        return SPOTIFY_TOKEN_CACHE["token"]

    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {auth_header}"},
        timeout=15
    )
    response.raise_for_status()
    token_data = response.json()

    SPOTIFY_TOKEN_CACHE["token"] = token_data["access_token"]
    SPOTIFY_TOKEN_CACHE["expires_at"] = now + token_data.get("expires_in", 3600)
    return SPOTIFY_TOKEN_CACHE["token"]


def _spotify_get(path, params=None):
    token = _spotify_get_access_token()
    url = f"https://api.spotify.com/v1{path}"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def _normalize_playlist_name(name):
    return name.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")


def buscar_playlist(query, market=None):
    params = {
        "q": query,
        "type": "playlist",
        "limit": 10
    }
    if market:
        params["market"] = market
    data = _spotify_get("/search", params=params)
    return data.get("playlists", {}).get("items", [])


def _playlists_to_tracks(playlists):
    if not playlists:
        return []

    playlist_id = playlists[0].get("id")
    if not playlist_id:
        return []

    tracks_data = _spotify_get(f"/playlists/{playlist_id}/tracks", {"limit": 10})
    items = tracks_data.get("items", [])
    tracks = []

    for item in items:
        track = item.get("track")
        if not track:
            continue
        artists = [artist.get("name", "") for artist in track.get("artists", [])]
        image_url = ""
        album_images = track.get("album", {}).get("images", [])
        if album_images:
            image_url = album_images[0].get("url", "")

        popularity = track.get("popularity")
        reproducciones = popularity * 1000 if isinstance(popularity, int) else 0

        tracks.append({
            "nombre_cancion": track.get("name", "N/D"),
            "nombre_artista": ", ".join(artists) or "N/D",
            "reproducciones": reproducciones,
            "imagen_artista": image_url
        })

    return tracks


def obtener_top_global_spotify():
    playlists = buscar_playlist("Top 50 Global", market=SPOTIFY_SEARCH_MARKET)
    if not playlists:
        playlists = buscar_playlist("Top 50", market=SPOTIFY_SEARCH_MARKET)
    return _playlists_to_tracks(playlists)


def obtener_top_pais_spotify(pais):
    country_code = COUNTRY_CODE_MAP.get(pais)
    if not country_code:
        return []

    playlists = buscar_playlist(f"Top 50 {pais}", market=country_code)
    if not playlists:
        playlists = buscar_playlist("Top 50", market=country_code)

    return _playlists_to_tracks(playlists)


def obtener_ciudades_por_pais(pais):
    return CITY_OPTIONS.get(pais, [])


def obtener_top_ciudad_spotify(pais, ciudad):
    country_code = COUNTRY_CODE_MAP.get(pais)
    query = f"Top 50 {ciudad}"
    playlists = buscar_playlist(query, market=country_code if country_code else SPOTIFY_SEARCH_MARKET)
    if not playlists:
        playlists = buscar_playlist(ciudad, market=country_code if country_code else SPOTIFY_SEARCH_MARKET)

    return _playlists_to_tracks(playlists)

def obtener_paises_disponibles():
    return list(COUNTRY_CODE_MAP.keys())
