import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from tafsir_mcp import get_tafsir

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tafsir Search API")

# Allow CORS for HuggingFace Spaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/api/search")
async def search_tafsir(req: SearchRequest):
    """API Endpoint to perform hybrid search on Tafsirs."""
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        result = await get_tafsir(req.query.strip(), top_k=req.top_k)
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {"results": result.get("tafsir_chunks", [])}
    except Exception as e:
        logger.error(f"Search API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Base directory
base_dir = os.path.dirname(__file__)

# Mount assets folder
assets_dir = os.path.join(base_dir, "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Serve index.html at root
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    path_to_file = os.path.join(base_dir, full_path)
    if os.path.isfile(path_to_file) and not full_path.startswith("api/"):
        return FileResponse(path_to_file)
    return FileResponse(os.path.join(base_dir, "index.html"))

# HF Spaces automatically runs uvicorn app:app if Gradio is selected
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)
