from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yt_dlp
import ssl
import os
try:
    from pytubefix import YouTube
    ssl._create_default_https_context = ssl._create_unverified_context
except ImportError:
    YouTube = None

router = APIRouter()

class VideoRequest(BaseModel):
    url: str

@router.post("/youtube-info")
async def youtube_info(request: VideoRequest):
    url = request.url
    print(f"DEBUG: Analyzing URL: {url}")
    
    # 1. Try pytubefix FIRST with SSL bypass (Verified to work in terminal)
    if YouTube:
        try:
            print("DEBUG: Attempting pytubefix...")
            yt = YouTube(url)
            # Force access to a property to trigger network request
            title = yt.title
            return {
                "title": title,
                "duration": yt.length,
                "video_id": yt.video_id,
                "thumbnail": yt.thumbnail_url
            }
        except Exception as e:
            print(f"DEBUG: pytubefix failed: {str(e)}")

    # 2. Try yt-dlp with explicit cookies.txt if it exists
    cookies_path = "cookies.txt"
    if os.path.exists(cookies_path):
        try:
            print("DEBUG: Using manual cookies.txt...")
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiefile': cookies_path,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "video_id": info.get('id'),
                    "thumbnail": info.get('thumbnail')
                }
        except Exception as e:
            print(f"DEBUG: cookies.txt failed: {str(e)}")

    # 3. Try yt-dlp with explicit browser cookie extraction
    browsers_to_try = ['safari', 'chrome', 'firefox', 'edge']
    last_error = ""

    for browser in browsers_to_try:
        try:
            print(f"DEBUG: Trying to borrow session from {browser}...")
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiesfrombrowser': (browser,),
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "video_id": info.get('id'),
                    "thumbnail": info.get('thumbnail')
                }
        except Exception as e:
            err_msg = str(e)
            print(f"DEBUG: Browser {browser} failed: {err_msg}")
            if "Permission denied" in err_msg or "Keychain" in err_msg:
                last_error = f"Error de permisos en {browser}. Por favor, dale 'Acceso total al disco' a la Terminal en Ajustes de Privacidad de tu Mac."
            else:
                last_error = err_msg
            continue

    # 3. Last stand: try mobile clients without cookies
    try:
        print("DEBUG: Final attempt with mobile client simulation...")
        ydl_opts = {
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['ios', 'mweb']}}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get('title'),
                "duration": info.get('duration'),
                "video_id": info.get('id'),
                "thumbnail": info.get('thumbnail')
            }
    except Exception as e:
        last_error = str(e)

    # If everything fails, provide a very human-friendly error
    raise HTTPException(
        status_code=400, 
        detail=f"No pudimos entrar a YouTube. Razones posibles:\n1. No tenés sesión iniciada en Chrome/Safari.\n2. macOS bloqueó el acceso (activá 'Acceso total al disco' para la Terminal).\n\nError técnico: {last_error}"
    )

@router.post("/estimate-time")
async def estimate_time(request: dict):
    return {"estimated_seconds": (request.get("duration", 0) / 10)}
