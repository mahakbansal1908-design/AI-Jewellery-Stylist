"""
app.py — FastAPI Backend for AI Jewellery Stylist MVP.
Serves the premium frontend and provides the /api/stylist endpoint.
"""
import os
import base64
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import the agent orchestrator
from agent_stylist import run_stylist_workflow

app = FastAPI(title="AI Jewellery Stylist MVP")

# Ensure static directory exists
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class StylistRequest(BaseModel):
    image: str  # base64 encoded image string


@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>AI Jewellery Stylist - Frontend Building...</h1>")
    return HTMLResponse(index_file.read_text(encoding="utf-8"))


@app.post("/api/stylist")
async def api_stylist(req: StylistRequest):
    try:
        # Clean base64 prefix if present (e.g., data:image/jpeg;base64,...)
        img_str = req.image
        if "," in img_str:
            img_str = img_str.split(",")[1]

        # Validate base64 string
        try:
            base64.b64decode(img_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")

        # Execute the Session 5 agent workflow
        result = await run_stylist_workflow(img_str, provider="g")
        return result

    except Exception as e:
        print(f"Error in stylist API: {e}")
        raise HTTPException(status_code=500, detail=str(e))


import json
from typing import List, Optional
from datetime import datetime

WARDROBE_FILE = Path(__file__).resolve().parent / "wardrobe.json"


class SavedItem(BaseModel):
    id: str
    outfit_type: str
    outfit_image: str
    jewellery_type: str
    style: str
    material: str
    finish_color: str
    styling_notes: str
    image_url: str
    saved_at: str


@app.get("/api/wardrobe", response_model=List[SavedItem])
async def get_wardrobe():
    if not WARDROBE_FILE.exists():
        return []
    try:
        data = json.loads(WARDROBE_FILE.read_text(encoding="utf-8"))
        return data
    except Exception:
        return []


@app.post("/api/wardrobe")
async def save_to_wardrobe(item: SavedItem):
    items = []
    if WARDROBE_FILE.exists():
        try:
            items = json.loads(WARDROBE_FILE.read_text(encoding="utf-8"))
        except Exception:
            items = []
    if not any(x["id"] == item.id for x in items):
        items.append(item.model_dump())
        WARDROBE_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")
    return {"status": "success", "items": items}


@app.delete("/api/wardrobe/{item_id}")
async def delete_from_wardrobe(item_id: str):
    if not WARDROBE_FILE.exists():
        return {"status": "success", "items": []}
    try:
        items = json.loads(WARDROBE_FILE.read_text(encoding="utf-8"))
        items = [x for x in items if x["id"] != item_id]
        WARDROBE_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return {"status": "success", "items": items}
    except Exception:
        return {"status": "error"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8105))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

