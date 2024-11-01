from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.static_manager import StaticManager
from src.blog_posts.hackmd import router as blog_router


app = FastAPI()
static_manager = StaticManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/backups")
async def list_backups(filename: str | None = None):
    """List all backups, optionally filtered by original filename."""
    return static_manager.list_backups(filename)

# Include your blog router
app.include_router(blog_router)