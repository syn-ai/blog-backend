from fastapi import FastAPI
from src.blog_posts.hackmd import router as blog_router

app = FastAPI()
app.include_router(blog_router)

if __name__ == "__main__":
    app.run("main:app", host="0.0.0.0", port=4050, reload=True)