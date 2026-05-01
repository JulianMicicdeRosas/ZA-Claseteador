import os
import asyncio
import json
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil
import yt_dlp
from faster_whisper import WhisperModel
import ssl
try:
    from pytubefix import YouTube
    ssl._create_default_https_context = ssl._create_unverified_context
except ImportError:
    YouTube = None

router = APIRouter()

class TranscribeRequest(BaseModel):
    video_id: str
    local_file: str = None

async def progress_stream(video_id: str, local_file: str = None):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    if local_file:
        audio_path = f"workspace/audio_cache/{local_file}"
    else:
        audio_path = f"workspace/audio_cache/{video_id}.mp3"
    
    if not os.path.exists(audio_path):
        yield f"data: {json.dumps({'status': 'downloading', 'progress': 0})}\n\n"
        
        success = False
        
        # 1. Try pytubefix for download
        if YouTube:
            try:
                print(f"DEBUG: Trying pytubefix download for {url}")
                yt = YouTube(url)
                stream = yt.streams.get_audio_only()
                if stream:
                    stream.download(output_path='workspace/audio_cache', filename=f"{video_id}.mp3")
                    success = True
            except Exception as e:
                print(f"DEBUG: pytubefix download failed: {str(e)}")

        # 2. Try manual cookies.txt if exists
        if not success and os.path.exists("cookies.txt"):
            try:
                print("DEBUG: Trying download with manual cookies.txt")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': f'workspace/audio_cache/{video_id}.%(ext)s',
                    'quiet': True,
                    'cookiefile': 'cookies.txt',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                success = True
            except Exception as e:
                print(f"DEBUG: cookies.txt download failed: {str(e)}")

        if not success:
            # 3. Try yt-dlp with browser cookies fallback
            browsers = ['chrome', 'safari', 'firefox', 'edge']
            for browser in browsers:
                try:
                    print(f"DEBUG: Trying download with cookies from {browser}")
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': f'workspace/audio_cache/{video_id}.%(ext)s',
                        'quiet': True,
                        'cookiesfrombrowser': (browser,),
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    success = True
                    break
                except:
                    continue

        if not success:
            yield f"data: {json.dumps({'status': 'error', 'detail': 'YouTube bloqueó la descarga. Por favor, asegúrate de tener sesión iniciada en tu navegador.'})}\n\n"
            return

        yield f"data: {json.dumps({'status': 'downloading', 'progress': 100})}\n\n"

    yield f"data: {json.dumps({'status': 'transcribing', 'progress': 0})}\n\n"
    
    model_size = "base"
    model = WhisperModel(model_size, device="auto", compute_type="float32")
    
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    transcription_text = ""
    total_duration = info.duration

    for segment in segments:
        m, s = divmod(int(segment.start), 60)
        h, m = divmod(m, 60)
        if h > 0:
            timecode = f"[{h:02d}:{m:02d}:{s:02d}]"
        else:
            timecode = f"[{m:02d}:{s:02d}]"
            
        line = f"{timecode} {segment.text.strip()}\n"
        transcription_text += line
        
        progress = (segment.end / total_duration) * 100
        yield f"data: {json.dumps({'status': 'transcribing', 'progress': min(progress, 99)})}\n\n"
        await asyncio.sleep(0.01)

    yield f"data: {json.dumps({'status': 'complete', 'transcription': transcription_text})}\n\n"

@router.post("/transcribe")
async def transcribe(request: TranscribeRequest):
    return StreamingResponse(progress_stream(request.video_id, request.local_file), media_type="text/event-stream")

@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    os.makedirs("workspace/audio_cache", exist_ok=True)
    file_path = os.path.join("workspace/audio_cache", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}
