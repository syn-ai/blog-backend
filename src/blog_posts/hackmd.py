import os
import json
from typing import List
import requests
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import HTTPException, APIRouter

load_dotenv()

HACKMD_API_URL = 'https://api.hackmd.io/v1'
router = APIRouter()

class BlogPost(BaseModel):
    id: str
    title: str
    content: str
    publishDate: str
    lastModified: str
    excerpt: str
    slug: str
    coverImage: str | None = None
    readingTime: str | None = None

def get_from_cache() -> List[BlogPost] | None:
    cache_path = Path("data/posts_cache.json")
    if cache_path.exists():
        return [BlogPost(**post) for post in json.loads(cache_path.read_text())]
    return None

def save_to_cache(posts: List[BlogPost]) -> None:
    cache_path = Path("data/posts_cache.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps([post.dict() for post in posts]))

@router.get("/posts", response_model=List[BlogPost])
async def fetch_blog_posts():
    # Try cache first
    cached_posts = get_from_cache()
    if cached_posts:
        return cached_posts

    # If not in cache, fetch from API
    headers = {"Authorization": f"Bearer {os.getenv('HACKMD_API_KEY')}"}
    
    try:
        response = requests.get(f"{HACKMD_API_URL}/notes", headers=headers)
        response.raise_for_status()
        posts = response.json()
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blog posts: {err}")

    # Transform to our BlogPost model
    transformed_posts = [
        BlogPost(
            id=post["id"],
            title=post["title"],
            content=post["content"],
            publishDate=post["publishedAt"],
            lastModified=post["lastChangedAt"],
            excerpt=post.get("excerpt") or post["content"][:150] + "...",
            slug=post["permalink"]
        ) for post in posts
    ]

    # Save to cache
    save_to_cache(transformed_posts)
    return transformed_posts

@router.get("/posts/{slug}", response_model=BlogPost)
async def fetch_blog_post(slug: str):
    # For single posts, we'll check the full cache first
    cached_posts = get_from_cache()
    if cached_posts:
        for post in cached_posts:
            if post.slug == slug:
                return post

    # If not found in cache, fetch from API
    headers = {"Authorization": f"Bearer {os.getenv('HACKMD_API_KEY')}"}
    
    try:
        response = requests.get(f"{HACKMD_API_URL}/notes/{slug}", headers=headers)
        response.raise_for_status()
        post = response.json()
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blog post: {err}")

    return BlogPost(
        id=post["id"],
        title=post["title"],
        content=post["content"],
        publishDate=post["publishedAt"],
        lastModified=post["lastChangedAt"],
        excerpt=post.get("excerpt") or post["content"][:150] + "...",
        slug=post["permalink"]
    )

@router.post("/posts/refresh", response_model=List[BlogPost])
async def refresh_blog_posts():
    posts = await fetch_blog_posts()
    save_to_cache(posts)
    return posts