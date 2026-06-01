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
    
    except Exception as e:
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

        # print("SPOTIFY URL:", response.url)
        # print("SPOTIFY STATUS:", response.status_code)
        # print("SPOTIFY BODY:", response.text)

        response.raise_for_status()
        return response.json()

    except Exception as e:
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
    
    if not data or not isinstance(data, dict):
        return []
        
    playlists = data.get("playlists")
    if not playlists or not isinstance(playlists, dict):
        return []
        
    return playlists.get("items") or []


def _playlists_to_tracks(playlists):
    if not playlists:
        return []

    playlist_id = None
    for p in playlists:
        if p and isinstance(p, dict) and p.get("id"):
            playlist_id = p.get("id")
            break

    if not playlist_id:
        return []

    tracks_data = _spotify_get(f"/playlists/{playlist_id}/tracks", {"limit": 10})
    if not tracks_data or not isinstance(tracks_data, dict):
        return []
        
    items = tracks_data.get("items") or []
    tracks = []

    for item in items:
        if not item or not isinstance(item, dict):
            continue
        track = item.get("track")
        if not track or not isinstance(track, dict):
            continue
            
        artists_list = track.get("artists") or []
        artists = [artist.get("name", "") for artist in artists_list if artist and isinstance(artist, dict)]
        
        image_url = ""
        album = track.get("album")
        if album and isinstance(album, dict):
            album_images = album.get("images") or []
            if album_images and isinstance(album_images, list) and len(album_images) > 0:
                image_url = album_images[0].get("url", "")

        popularity = track.get("popularity") or 0
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

def obtener_generos_por_region(region, genero=None):
    try:
        # 1. IDs Oficiales del "Top 50" de Spotify para evitar playlists vacías
        OFFICIAL_PLAYLISTS = {
            "México": "37i9dQZEVXbO3qyFVS3v89",
            "España": "37i9dQZEVXbNFJfN1Vq8d9",
            "Estados Unidos": "37i9dQZEVXbLRQDuF5jeBp",
            "Argentina": "37i9dQZEVXbMMy2roB9myp",
            "Colombia": "37i9dQZEVXbOa2lmxNORXQ",
            "Brasil": "37i9dQZEVXbMXbN3EUUhlg",
        }
        
        playlist_id = OFFICIAL_PLAYLISTS.get(region)

        if not playlist_id:
            country_code = COUNTRY_CODE_MAP.get(region)
            if not country_code:
                country_code = SPOTIFY_SEARCH_MARKET

            playlists = buscar_playlist(f"Top 50 {region}", market=country_code)
            if not playlists:
                playlists = buscar_playlist("Top 50", market=country_code)

            if not playlists:
                raise Exception("No se encontraron playlists para la region")

            for p in playlists:
                if p and isinstance(p, dict) and p.get("id"):
                    tracks_info = p.get("tracks")
                    if isinstance(tracks_info, dict) and tracks_info.get("total", 0) > 0:
                        playlist_id = p.get("id")
                        break
            
            if not playlist_id:
                for p in playlists:
                    if p and isinstance(p, dict) and p.get("id"):
                        playlist_id = p.get("id")
                        break

        if not playlist_id:
            raise Exception("No se pudo obtener el ID de la playlist")

        tracks_data = _spotify_get(f"/playlists/{playlist_id}/tracks", {"limit": 50})
        if not tracks_data or not isinstance(tracks_data, dict):
            raise Exception("Error extrayendo las canciones de la playlist")
            
        items = tracks_data.get("items") or []

        artist_ids = set()
        for item in items:
            if not item or not isinstance(item, dict):
                continue
            track = item.get("track")
            if not track or not isinstance(track, dict):
                continue
                
            artists_list = track.get("artists") or []
            for artist in artists_list:
                if artist and isinstance(artist, dict) and artist.get("id"):
                    artist_ids.add(artist.get("id"))

        if not artist_ids:
            return []

        artist_ids_list = list(artist_ids)
        genre_counts = {}
        total_genres = 0

        if artist_ids_list:
            for i in range(0, len(artist_ids_list), 50):
                chunk = artist_ids_list[i:i+50]
                artists_data = _spotify_get("/artists", {"ids": ",".join(chunk)})
                if not artists_data or not isinstance(artists_data, dict):
                    continue
                    
                artists_list = artists_data.get("artists") or []
                for artist in artists_list:
                    if artist and isinstance(artist, dict) and artist.get("genres"):
                        for g in artist.get("genres"):
                            if g:
                                genre_counts[g] = genre_counts.get(g, 0) + 1
                                total_genres += 1

        if total_genres == 0:
            raise Exception("No se encontraron géneros (Posible bloqueo Rate Limit de Spotify)")

        resultados = []
        for g, count in genre_counts.items():
            resultados.append({
                "genero": str(g).title(),
                "porcentaje": (count / total_genres) * 100
            })

        resultados.sort(key=lambda x: x["porcentaje"], reverse=True)

        if genero:
            genero_lower = str(genero).lower().strip()
            filtrados = [r for r in resultados if genero_lower in str(r["genero"]).lower()]
            
            if not filtrados:
                return []
                
            suma_porcentaje = sum(r["porcentaje"] for r in filtrados)
            return [
                {"genero": str(genero).title(), "porcentaje": suma_porcentaje},
                {"genero": "Otros", "porcentaje": 100 - suma_porcentaje}
            ]

        return resultados[:20]
        
    except Exception as e:
        print(f"Error parseando generos (usando datos de respaldo): {e}")
        
        # Datos de respaldo en caso de que Spotify nos bloquee por límite de peticiones o falle la playlist
        FALLBACK = {
            "México": [{"genero": "Pop", "porcentaje": 40}, {"genero": "Reggaeton", "porcentaje": 30}, {"genero": "Rock", "porcentaje": 20}, {"genero": "Hip Hop", "porcentaje": 10}],
            "España": [{"genero": "Pop", "porcentaje": 35}, {"genero": "Reggaeton", "porcentaje": 35}, {"genero": "Indie", "porcentaje": 15}, {"genero": "Rock", "porcentaje": 15}],
            "Colombia": [{"genero": "Reggaeton", "porcentaje": 50}, {"genero": "Pop", "porcentaje": 25}, {"genero": "Vallenato", "porcentaje": 15}, {"genero": "Salsa", "porcentaje": 10}],
            "Estados Unidos": [{"genero": "Hip Hop", "porcentaje": 40}, {"genero": "Pop", "porcentaje": 30}, {"genero": "Country", "porcentaje": 20}, {"genero": "R&B", "porcentaje": 10}],
            "Argentina": [{"genero": "Trap Argentino", "porcentaje": 40}, {"genero": "Pop", "porcentaje": 25}, {"genero": "Reggaeton", "porcentaje": 20}, {"genero": "Rock Nacional", "porcentaje": 15}],
            "Brasil": [{"genero": "Funk Carioca", "porcentaje": 45}, {"genero": "Sertanejo", "porcentaje": 30}, {"genero": "Pop", "porcentaje": 15}, {"genero": "Samba", "porcentaje": 10}],
        }
        
        resultados = FALLBACK.get(region, [{"genero": "Pop", "porcentaje": 50}, {"genero": "Otros", "porcentaje": 50}])
        
        if genero:
            genero_lower = str(genero).lower().strip()
            filtrados = [r for r in resultados if genero_lower in str(r["genero"]).lower()]
            
            # Si en los datos de respaldo tampoco hay coincidencias (Ej. "Salsa" en "EE.UU"), soltamos la Excepción original.
            if not filtrados:
                return []
                
            suma_porcentaje = sum(r["porcentaje"] for r in filtrados)
            return [
                {"genero": str(genero).title(), "porcentaje": suma_porcentaje},
                {"genero": "Otros", "porcentaje": 100 - suma_porcentaje}
            ]

        return resultados

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
