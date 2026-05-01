import os
import aiohttp
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json

router = APIRouter()

class PublishRequest(BaseModel):
    html: str
    filename: str
    wp_config: dict = None

@router.post("/save-local")
async def save_local(request: PublishRequest):
    try:
        path = os.path.join("workspace/downloads", request.filename)
        with open(path, "w") as f:
            f.write(request.html)
        
        # Also save as txt if it's just the transcription? 
        # For now just the HTML as requested.
        return {"status": "ok", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish-wordpress")
async def publish_wordpress(request: PublishRequest):
    if not request.wp_config:
        raise HTTPException(status_code=400, detail="Missing WP configuration")
    
    cfg = request.wp_config
    url = f"{cfg['url'].rstrip('/')}/wp-json/wp/v2/media"
    user = cfg['user']
    password = cfg['app_password']
    
    auth_str = f"{user}:{password}"
    auth_bytes = auth_str.encode("ascii")
    base64_auth = base64.b64encode(auth_bytes).decode("ascii")
    
    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Disposition": f'attachment; filename="{request.filename}"',
        "Content-Type": "text/html"
    }
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, data=request.html, headers=headers) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    return {"status": "ok", "url": data.get("source_url")}
                else:
                    err_text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=err_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
