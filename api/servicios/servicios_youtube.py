import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
REGIONES = ["MX"]
CACHE_FILE = "youtube_ids_cache.json"

def cargar_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def buscar_metricas_youtube(nombre_artista):
    if not YOUTUBE_API_KEY:
        return {
            "vistas": 0,
            "likes": 0,
            "regiones": []
        }

    cache = cargar_cache()
    total_vistas = 0
    total_likes = 0
    regiones = []

    try:
        for region in REGIONES:
            cache_key = f"{nombre_artista}_{region}"
            video_ids = cache.get(cache_key)

            if not video_ids:
                search_response = requests.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": f"{nombre_artista} official music video",
                        "type": "video",
                        "regionCode": region,
                        "maxResults": 3,
                        "key": YOUTUBE_API_KEY
                    },
                    timeout=15
                )
                search_response.raise_for_status()
                search_data = search_response.json()

                video_ids = [
                    item["id"]["videoId"]
                    for item in search_data.get("items", [])
                    if "videoId" in item.get("id", {})
                ]

                if video_ids:
                    cache[cache_key] = video_ids
                    guardar_cache(cache)

            if not video_ids:
                continue

            stats_response = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics",
                    "id": ",".join(video_ids),
                    "key": YOUTUBE_API_KEY
                },
                timeout=15
            )
            stats_response.raise_for_status()
            stats_data = stats_response.json()

            vistas_region = 0
            likes_region = 0

            for item in stats_data.get("items", []):
                stats = item.get("statistics", {})
                vistas_region += int(stats.get("viewCount", 0))
                likes_region += int(stats.get("likeCount", 0))

            total_vistas += vistas_region
            total_likes += likes_region

            popularidad_region = vistas_region * 0.7 + likes_region * 0.3

            regiones.append({
                "codigo": region,
                "vistas": vistas_region,
                "likes": likes_region,
                "popularidad_region": round(popularidad_region, 2)
            })
        
    except Exception:
        pass

    return {
        "vistas": total_vistas,
        "likes": total_likes,
        "regiones": regiones
    }