import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.routes import system, youtube, transcribe, format_route, publish, config, session as session_route
from jinja2 import Environment, FileSystemLoader

app = FastAPI(title="Zorro Azul Transcriptor")

# ... middleware ...

# Routes
app.include_router(system.router, prefix="/api")
app.include_router(youtube.router, prefix="/api")
app.include_router(transcribe.router, prefix="/api")
app.include_router(format_route.router, prefix="/api")
app.include_router(publish.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(session_route.router, prefix="/api")

# Static files for the UI
# We'll serve the UI from app/ui
app.mount("/static", StaticFiles(directory="app/ui"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("app/ui/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7860)
