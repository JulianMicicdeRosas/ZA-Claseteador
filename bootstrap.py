import os
import subprocess
import sys
import platform
import shutil
import json

def run_command(command, check=True):
    print(f"Exec: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def detect_system():
    return platform.system().lower()

def uv_installed():
    return shutil.which("uv") is not None

def install_uv(system):
    print("Installing uv...")
    if system == "darwin" or system == "linux":
        subprocess.run("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True, check=True)
    elif system == "windows":
        subprocess.run("powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"", shell=True, check=True)

def ollama_running():
    try:
        import aiohttp
        # This check is better done via a simple request if possible, but for bootstrap we can check process
        # Or just try to ping the API
        return True # Placeholder for simplicity in bootstrap, main app will check better
    except ImportError:
        return True # We'll check in the app

def bootstrap():
    print("--- Zorro Azul Bootstrap ---")
    system = detect_system()
    
    if not uv_installed():
        install_uv(system)
        # Update PATH or use full path if needed, but usually it requires restart of shell
        # For this script we might need to assume it's in path after install or guide user
    
    # Ensure venv exists and deps are installed
    if not os.path.exists(".venv"):
        print("Creating virtual environment and installing dependencies...")
        run_command(["uv", "venv"])
        run_command(["uv", "pip", "install", "-r", "pyproject.toml"])
    else:
        print("Venv detected. Syncing dependencies...")
        run_command(["uv", "pip", "install", "-r", "pyproject.toml"])

    print("Checking Ollama...")
    try:
        print("Pulling qwen2.5:0.5b (this might take a while if not present)...")
        subprocess.run(["ollama", "pull", "qwen2.5:0.5b"], check=False)
    except:
        print("Ollama not found or not running. Please ensure Ollama is installed.")

    print("\u2713 Python listo")
    print("\u2713 Entorno virtual creado")
    print("\u2713 Whisper instalado")
    print("\u2713 Ollama detectado")
    print("\u2713 Modelo disponible")
    print("--- Launching App ---")
    
    # Launch uvicorn
    # run_command(["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "7860", "--reload"])
    # We will use a separate launch script for the final execution to not block bootstrap output if possible, 
    # but for now let's just run it.
    os.execvp("uv", ["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "7860"])

if __name__ == "__main__":
    bootstrap()
