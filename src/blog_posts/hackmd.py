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
    """
    Pydantic model representing a blog post.
    
    Attributes:
        id: Unique identifier for the post
        title: Title of the blog post
        content: Full content of the blog post
        publishDate: Date when the post was published
        lastModified: Date when the post was last modified
        excerpt: Short summary of the post content
        slug: URL-friendly identifier for the post
        coverImage: Optional URL to the post's cover image
        readingTime: Optional estimated reading time
    """
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
    """
    Retrieve blog posts from the local cache file.
    
    Returns:
        List[BlogPost]: List of cached blog posts if cache exists
        None: If cache doesn't exist or is invalid
    """
    cache_path = Path("data/posts_cache.json")
    if cache_path.exists():
        return [BlogPost(**post) for post in json.loads(cache_path.read_text())]
    return None

def save_to_cache(posts: List[BlogPost]) -> None:
    """
    Save blog posts to the local cache file.
    
    Args:
        posts: List of BlogPost objects to cache
    """
    cache_path = Path("data/posts_cache.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps([post.dict() for post in posts]))

@router.get("/posts", response_model=List[BlogPost])
async def fetch_blog_posts():
    """
    Fetch all blog posts from cache or HackMD API.
    
    Returns:
        List[BlogPost]: List of all blog posts
        
    Raises:
        HTTPException: If API request fails or returns invalid data
    """
    if cached_posts := get_from_cache():
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
    """
    Fetch a single blog post by its slug.
    
    Args:
        slug: URL-friendly identifier for the post
        
    Returns:
        BlogPost: Single blog post matching the slug
        
    Raises:
        HTTPException: If post not found or API request fails
    """
    if cached_posts := get_from_cache():
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
    """
    Force refresh of blog posts cache.
    
    Returns:
        List[BlogPost]: Updated list of all blog posts
        
    Raises:
        HTTPException: If refresh operation fails
    """
    posts = await fetch_blog_posts()
    save_to_cache(posts)
    return posts 