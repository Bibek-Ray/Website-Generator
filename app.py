# backend/app.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from backend.manager_agent import ManagerAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, etc.) from the "frontend" folder
app.mount("/public", StaticFiles(directory="frontend/public"), name="public")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve the main index.html at the root
@app.get("/")
def serve_home():
    return FileResponse(os.path.join("frontend", "index.html"))

# Global ManagerAgent instance to maintain conversation state
manager_agent = ManagerAgent()

def combine_html_css(html: str, css: str) -> str:
    """
    Combines HTML and CSS by injecting the CSS into the HTML head section.
    If a </head> tag exists, insert before it.
    Otherwise, append a <style> tag at the beginning.
    """
    lower_html = html.lower()
    head_index = lower_html.find("</head>")
    style_tag = f"<style>{css}</style>"
    if head_index != -1:
        return html[:head_index] + style_tag + html[head_index:]
    else:
        return style_tag + html

@app.post("/generate")
async def generate_site(request: Request):
    """
    Expects a JSON payload:
    {
      "user_prompt": "Your website requirements here"
    }
    Calls the ManagerAgent to generate the site in a single pass.
    """
    data = await request.json()
    user_prompt = data.get("user_prompt")
    if not user_prompt:
        raise HTTPException(status_code=400, detail="user_prompt not provided")
    
    try:
        html, css = manager_agent.generate_site(user_prompt)
        inline_html = combine_html_css(html, css)
        return JSONResponse(content={"html": html, "css": css, "inline_html": inline_html})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation")
async def conversation_endpoint(request: Request):
    """
    Expects a JSON payload:
    {
      "message": "Instructions for revising the site",
      "html": "Current HTML",
      "css": "Current CSS"
    }

    This endpoint always revises the current site using ManagerAgent.revise_site.
    Returns updated HTML/CSS + inline_html.
    """
    data = await request.json()
    message = data.get("message")
    html = data.get("html")
    css = data.get("css")

    if not message:
        raise HTTPException(status_code=400, detail="message not provided")

    if not html or not css:
        raise HTTPException(status_code=400, detail="HTML and CSS required for revision.")

    print("Incoming revision request:", message[:100], "...")  # Truncate long messages
    print("HTML received:", html is not None, "| CSS received:", css is not None)

    revised_html, revised_css = manager_agent.revise_site(message, html, css)
    inline_html = combine_html_css(revised_html, revised_css)
    reply = "Revisions applied based on your feedback."

    return JSONResponse(content={
        "reply": reply,
        "html": revised_html,
        "css": revised_css,
        "inline_html": inline_html
    })

@app.get("/site/{site_id}")
async def get_site(site_id: str):
    """
    Serves a previously generated HTML file based on the site_id.
    """
    file_path = os.path.join("generated_sites", f"site_{site_id}", "index.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Site not found")
    return FileResponse(file_path, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)