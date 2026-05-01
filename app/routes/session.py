import os
import json
from fastapi import APIRouter, HTTPException

router = APIRouter()

SESSION_PATH = "workspace/current_session.json"

@router.get("/session")
async def get_session():
    if not os.path.exists(SESSION_PATH):
        return {}
    with open(SESSION_PATH, "r") as f:
        return json.load(f)

@router.post("/session")
async def save_session(session: dict):
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w") as f:
        json.dump(session, f)
    return {"status": "ok"}
