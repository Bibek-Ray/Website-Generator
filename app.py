from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import uuid
from backend.generator import generate_frontend_site, save_generated_site

import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (e.g., CSS, JS) from the "frontend" folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_home():
    """Serve the main index.html file at the root URL."""
    return FileResponse(os.path.join("frontend", "index.html"))

@app.post("/generate")
async def generate_site(request: Request):
    """
    Expects a JSON payload:
    {
      "user_prompt": "your website requirements here"
    }
    """
    data = await request.json()
    user_prompt = data.get("user_prompt")
    if not user_prompt:
        raise HTTPException(status_code=400, detail="user_prompt not provided")
    
    try:
        html, css = generate_frontend_site(user_prompt)
        # Generate a unique site id (first 8 characters of a uuid)
        return JSONResponse(content={"html": html, "css": css})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/site/{site_id}")
async def get_site(site_id: str):
    """
    Serves the generated HTML file.
    """
    file_path = os.path.join("generated_sites", f"site_{site_id}", "index.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Site not found")
    return FileResponse(file_path, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)