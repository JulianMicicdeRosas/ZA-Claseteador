import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

CONFIG_PATH = os.path.expanduser("~/.zorroazul-transcriptor/config.json")

def ensure_config_dir():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

@router.get("/config")
async def get_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        # Remove sensitive data before returning to UI?
        # The prompt says "sin password"
        if "wp_app_password" in config:
            config["wp_app_password"] = "****"
        return config

@router.put("/config")
async def update_config(config: dict):
    ensure_config_dir()
    # If password is **** it means it wasn't changed
    if config.get("wp_app_password") == "****" and os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            old_config = json.load(f)
            config["wp_app_password"] = old_config.get("wp_app_password")
            
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
    return {"status": "ok"}

@router.get("/prompt")
async def get_prompt():
    with open("prompts/default_prompt.md", "r") as f:
        return {"prompt": f.read()}

@router.put("/prompt")
async def update_prompt(request: dict):
    with open("prompts/default_prompt.md", "w") as f:
        f.write(request.get("prompt", ""))
    return {"status": "ok"}

@router.get("/template")
async def get_template():
    with open("templates/base.html", "r") as f:
        return {"template": f.read()}

@router.put("/template")
async def update_template(request: dict):
    with open("templates/base.html", "w") as f:
        f.write(request.get("template", ""))
    return {"status": "ok"}
