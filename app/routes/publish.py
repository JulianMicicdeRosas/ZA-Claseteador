import os
import aiohttp
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class PublishRequest(BaseModel):
    html: str
    filename: str
    wp_config: dict = None
    clase_num: Optional[int] = None
    video_url: Optional[str] = None

@router.post("/save-local")
async def save_local(request: PublishRequest):
    try:
        path = os.path.join("workspace/downloads", request.filename)
        with open(path, "w") as f:
            f.write(request.html)
        return {"status": "ok", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish-wordpress")
async def publish_wordpress(request: PublishRequest):
    if not request.wp_config:
        raise HTTPException(status_code=400, detail="Missing WP configuration")

    cfg = request.wp_config
    base_url = cfg['url'].rstrip('/')
    user = cfg['user']
    password = cfg['app_password']

    auth_str = f"{user}:{password}"
    base64_auth = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
    auth_header = f"Basic {base64_auth}"

    media_headers = {
        "Authorization": auth_header,
        "Content-Disposition": f'attachment; filename="{request.filename}"',
        "Content-Type": "text/html"
    }

    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # 1. Subir archivo a WordPress Media
            async with session.post(
                f"{base_url}/wp-json/wp/v2/media",
                data=request.html,
                headers=media_headers
            ) as resp:
                if resp.status not in [200, 201]:
                    err_text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=err_text)
                media_data = await resp.json()
                source_url = media_data.get("source_url")

            # 2. Crear redirección en el plugin Redirection (best-effort)
            redirect_result = None
            if request.clase_num and request.video_url:
                redirect_result = await _create_redirection(
                    session=session,
                    base_url=base_url,
                    auth_header=auth_header,
                    source=f"/video-clase-{request.clase_num}",
                    target=request.video_url
                )

        return {
            "status": "ok",
            "url": source_url,
            "redirect": redirect_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _create_redirection(session, base_url, auth_header, source, target):
    url = f"{base_url}/wp-json/redirection/v1/redirect"
    payload = {
        "url": source,
        "action_type": "url",
        "action_code": 301,
        "group_id": 1,
        "action_data": {"url": target},
        "match_data": {
            "source": {
                "flag_regex": False,
                "flag_trailing": True,
                "flag_case": False,
                "flag_query": "exact"
            }
        }
    }
    try:
        async with session.post(
            url,
            json=payload,
            headers={"Authorization": auth_header, "Content-Type": "application/json"}
        ) as resp:
            data = await resp.json()
            if resp.status in [200, 201]:
                return {"status": "ok", "source": source, "target": target}
            else:
                return {"status": "error", "detail": data}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
