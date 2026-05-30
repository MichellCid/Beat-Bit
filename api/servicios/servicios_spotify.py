import os
import base64
import time
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

#SPOTIFY_SEARCH_MARKET = os.getenv("SPOTIFY_SEARCH_MARKET", "MX")

SPOTIFY_BASE_URL = "https://api.spotify.com/v1"

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
    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {auth_header}"},
            timeout=15
        )
    
   
        response.raise_for_status()
        token_data = response.json()
        print("TOKEN RESPONSE:", token_data)

        SPOTIFY_TOKEN_CACHE["token"] = token_data["access_token"]
        SPOTIFY_TOKEN_CACHE["expires_at"] = now + token_data.get("expires_in", 3600)
        return SPOTIFY_TOKEN_CACHE["token"]
    
    except requests.exceptions.RequestException as e:
        print("error token")
        return None


#def _spotify_get(path, params=None):
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


#def _spotify_get(path, params=None):
    token = _spotify_get_access_token()
    url = f"https://api.spotify.com/v1{path}"

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        },
        params=params,
        timeout=15
    )

    print("SPOTIFY URL:", response.url)
    print("SPOTIFY STATUS:", response.status_code)
    print("SPOTIFY BODY:", response.text)

    response.raise_for_status()
    return response.json()


def _spotify_get(path, params=None):
    token = _spotify_get_access_token()

    if not token:
        return {}

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"{SPOTIFY_BASE_URL}{path}"

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        print("SPOTIFY URL:", response.url)
        print("SPOTIFY STATUS:", response.status_code)
        print("SPOTIFY BODY:", response.text)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("ERROR SPOTIFY GET:", e)
        return {}


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

#-----------------------------------------------------------------------------------------------------------------------------------
# peticiones para datos del artista

def busquedaArtista(nombre):
    data = _spotify_get("/search", {
        "q": nombre,
        "type": "artist",
        "limit": 1
    })

    artistas = data.get("artists", {}).get("items", [])

    if not artistas:
        return None

    artistaBase = artistas[0]

    artist_id = artistaBase.get("id")

    artista = _spotify_get(f"/artists/{artist_id}")
    print("ARTISTA DETALLADO:", artista)


    imagen = ""
    if artista.get("images"):
        imagen = artista["images"][0].get("url", "")

    return {
        "id": artista.get("id"),
        "nombre": artista.get("name"),
        "seguidores": artista.get("followers", {}).get("total", 0),
        "popularidad": artista.get("popularity", 0),
        "generos": artista.get("genres", []),
        "imagen": imagen
    }


# def obtenerTopCancionesArtista(artist_id):
#     data = _spotify_get(
#         f"/artists/{artist_id}/top-tracks",
#         {"market": SPOTIFY_SEARCH_MARKET}
#     )

#     canciones = []

#     for track in data.get("tracks", [])[:10]:
#         imagen_album = ""

#         if track.get("album", {}).get("images"):
#             imagen_album = track["album"]["images"][0].get("url", "")

#         canciones.append({
#             "id": track.get("id"),
#             "nombre": track.get("name"),
#             "album": track.get("album", {}).get("name", "N/D"),
#             "popularidad": track.get("popularity", 0),
#             "imagen_album": imagen_album
#         })

#     return canciones

def obtenerTopCancionesArtista(nombre_artista):

    data = _spotify_get("/search", {
        "q": f"artist:{nombre_artista}",
        "type": "track",
        "limit": 10,
        "market": SPOTIFY_SEARCH_MARKET
    })

    canciones = []

    for track in data.get("tracks", {}).get("items", []):

        imagen_album = ""

        if track.get("album", {}).get("images"):
            imagen_album = track["album"]["images"][0].get("url", "")

        canciones.append({
            "id": track.get("id"),
            "nombre": track.get("name"),
            "album": track.get("album", {}).get("name", "N/D"),
            "popularidad": track.get("popularity", 0),
            "imagen_album": imagen_album
        })

    canciones.sort(
        key=lambda c: c.get("popularidad", 0),
        reverse=True
    )

    return canciones

def obtenerCancionMasPopular(canciones):
    if not canciones:
        return {
            "nombre": "No disponible",
            "popularidad": 0,
            "album": "No disponible",
            "imagen_album": ""
        }

    return max(canciones, key=lambda c: c.get("popularidad", 0))




def obtenerAlbumPopular(canciones):
    if not canciones:
        return {
            "nombre": "No disponible",
            "imagen": ""
        }

    cancion_top = obtenerCancionMasPopular(canciones)

    return {
        "nombre": cancion_top.get("album", "No disponible"),
        "imagen": cancion_top.get("imagen_album", "")
    }
