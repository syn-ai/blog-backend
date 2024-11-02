import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.static_manager import StaticManager
from src.blog_posts.hackmd import router as blog_router

app = FastAPI()
static_manager = StaticManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000", "https://blog-synai.ngrok.dev", "https://blogbackend-synai.ngrok.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "x-api-key"], 
    expose_headers=["*"], 
)

app.include_router(blog_router)

@app.get("/api/backups")
async def list_backups(filename: str | None = None):
    """List all backups, optionally filtered by original filename."""
    return static_manager.list_backups(filename)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=4050, reload=True)