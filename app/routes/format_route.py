import aiohttp
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from jinja2 import Template
import os

router = APIRouter()

class FormatRequest(BaseModel):
    transcription: str
    model_name: str = "gemma4:latest"

class PreviewRequest(BaseModel):
    articles_html: str
    metadata: dict

@router.post("/format")
async def format_transcription(request: FormatRequest):
    with open("prompts/default_prompt.md", "r") as f:
        system_prompt = f.read()

    # Chunking logic: Split by words to stay within context limits
    words = request.transcription.split()
    chunk_size = 2500  # Words per chunk
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    
    async def generate_format():
        final_html = ""
        timeout = aiohttp.ClientTimeout(total=600) # Higher timeout for multiple chunks
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for i, chunk in enumerate(chunks):
                # Send progress
                progress = int(((i) / len(chunks)) * 100)
                yield f"data: {json.dumps({'status': f'Procesando parte {i+1} de {len(chunks)}', 'progress': progress})}\n\n"
                
                # If multiple chunks, add context
                context_prefix = f"ESTE ES EL FRAGMENTO {i+1} DE {len(chunks)} DE LA CLASE.\n\n" if len(chunks) > 1 else ""
                chunk_prompt = f"{system_prompt}\n\n{context_prefix}TRANSCRIPCIÓN:\n{chunk}"
                
                payload = {
                    "model": request.model_name,
                    "prompt": chunk_prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": 16384, # Increase context for larger models
                        "temperature": 0.2
                    }
                }
                
                try:
                    async with session.post("http://localhost:11434/api/generate", json=payload) as resp:
                        if resp.status != 200:
                            err_text = await resp.text()
                            yield f"data: {json.dumps({'status': 'error', 'detail': f'Error en Ollama: {err_text}'})}\n\n"
                            return
                        
                        data = await resp.json()
                        chunk_response = data.get("response", "").strip()
                        
                        if not chunk_response:
                            continue

                        # Robust Markdown Cleanup
                        import re
                        chunk_response = re.sub(r"^```[a-z]*\n?", "", chunk_response, flags=re.MULTILINE)
                        chunk_response = re.sub(r"\n?```$", "", chunk_response, flags=re.MULTILINE)
                        
                        final_html += chunk_response + "\n"
                except Exception as e:
                    yield f"data: {json.dumps({'status': 'error', 'detail': str(e)})}\n\n"
                    return

            if not final_html.strip():
                # FALLBACK: Try one last time with a very simple prompt if chunking failed
                yield f"data: {json.dumps({'status': 'Aplicando fallback...', 'progress': 90})}\n\n"
                fallback_prompt = f"Resume esta clase en formato HTML usando bloques <article>:\n\n{request.transcription[:5000]}"
                payload = {"model": request.model_name, "prompt": fallback_prompt, "stream": False}
                async with session.post("http://localhost:11434/api/generate", json=payload) as resp:
                    data = await resp.json()
                    final_html = data.get("response", "").strip()

            if not final_html.strip():
                yield f"data: {json.dumps({'status': 'error', 'detail': 'La IA no generó contenido.'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'completado', 'progress': 100, 'articles_html': final_html.strip()})}\n\n"

    return StreamingResponse(generate_format(), media_type="text/event-stream")

@router.post("/render-preview")
async def render_preview(request: PreviewRequest):
    try:
        with open("templates/base.html", "r") as f:
            template_str = f.read()
        template = Template(template_str)
        m = request.metadata
        html_final = template.render(
            tab_title=m.get("tab_title", ""),
            super_label=m.get("super_label", ""),
            main_title=m.get("main_title", ""),
            taught_by=m.get("taught_by", ""),
            reviewed_by=m.get("reviewed_by", ""),
            show_credits=m.get("show_credits", True),
            content=request.articles_html,
            video_id=m.get("video_id", ""),
            video_url=f"https://www.youtube.com/watch?v={m.get('video_id', '')}"
        )
        return {"html": html_final}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
