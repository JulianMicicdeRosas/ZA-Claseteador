from fastapi import APIRouter
import platform
import shutil
import subprocess

router = APIRouter()

@router.get("/system-check")
async def system_check():
    # Basic checks
    python_version = platform.python_version()
    
    # Check for whisper (faster-whisper)
    try:
        from faster_whisper import WhisperModel
        whisper_ok = True
        whisper_version = "1.0.3" # Placeholder or dynamic
    except ImportError:
        whisper_ok = False
        whisper_version = "None"

    # Check for ollama
    ollama_ok = False
    try:
        # Check if ollama command exists
        ollama_path = shutil.which("ollama")
        if ollama_path:
            # Check if service is running by pinging localhost:11434/api/tags
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags") as resp:
                    if resp.status == 200:
                        ollama_ok = True
    except:
        pass

    # Check for GPU
    gpu_type = "cpu"
    # Placeholder GPU detection
    if platform.system() == "Darwin":
        gpu_type = "metal"
    else:
        # Check for nvidia-smi?
        if shutil.which("nvidia-smi"):
            gpu_type = "cuda"

    return {
        "python": {"ok": True, "version": python_version},
        "whisper": {"ok": whisper_ok, "version": whisper_version},
        "ollama": {"ok": ollama_ok, "running": ollama_ok},
        "gemma": {"ok": ollama_ok, "model": "gemma4:latest"}, # Using Gemma 2 9B (gemma4)
        "gpu": {"ok": gpu_type != "cpu", "type": gpu_type},
        "ready": whisper_ok and ollama_ok
    }
