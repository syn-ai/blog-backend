import os
import json
from typing import List, Optional, Any
import requests
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import HTTPException, APIRouter, Header, Depends

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
    publishDate: Optional[int]=None
    lastModified: Optional[int]=None
    excerpt: str
    slug: str
    coverImage: str | None = None
    readingTime: str | None = None
    
def health_check(api_key: str) -> Any:
    url = f"{HACKMD_API_URL}/me"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    return HTTPException(response.status_code, response.text)

def get_from_cache() -> List[BlogPost] | None:
    """
    Retrieve blog notes from the local cache file.
    
    Returns:
        List[BlogPost]: List of cached blog notes if cache exists
        None: If cache doesn't exist or is invalid
    """
    cache_path = Path("data/notes_cache.json")
    if cache_path.exists():
        return [BlogPost(**post) for post in json.loads(cache_path.read_text())]
    return None

def save_to_cache(notes: List[BlogPost]) -> None:
    """
    Save blog notes to the local cache file.
    
    Args:
        notes: List of BlogPost objects to cache
    """
    cache_path = Path("data/notes_cache.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps([post.dict() for post in notes]))

def transform_note(post: dict) -> BlogPost:
    """
    Transform HackMD API response to BlogPost model.
    
    Args:
        post: Raw post data from HackMD API
        
    Returns:
        BlogPost: Transformed blog post
    """
    return BlogPost(
        id=post["id"],
        title=post["title"],
        content=post.get("content", ""),
        publishDate=post.get("publishedAt", post.get("createdAt", "")),
        lastModified=post.get("lastChangedAt", ""),
        excerpt=post.get("excerpt") or post.get("content", "")[:200] + "...",
        slug=post.get("permalink") or post.get("shortId", ""),
        coverImage=post.get("coverImage"),
        readingTime=post.get("readingTime")
    )

@router.get("/notes", response_model=List[BlogPost])
async def fetch_blog_notes():
    """
    Fetch all blog notes from cache or HackMD API.
    
    Args:
        api_key: Verified API key from header
    
    Returns:
        List[BlogPost]: List of all blog notes
        
    Raises:
        HTTPException: If API request fails or returns invalid data
    """
    try:
        if cached_notes := get_from_cache():
            return cached_notes

        headers = {"Authorization": f"Bearer {os.getenv('HACKMD_API_KEY')}"}

        try:
            response = requests.get(f"{HACKMD_API_URL}/notes", headers=headers)
            response.raise_for_status()
            note_list = response.json()

            # Fetch full content for each note
            posts = []
            for note in note_list:
                detail_response = requests.get(
                    f"{HACKMD_API_URL}/notes/{note['shortId']}", 
                    headers=headers
                )
                detail_response.raise_for_status()
                posts.append(detail_response.json())

        except requests.exceptions.RequestException as err:
            raise HTTPException(status_code=500, detail=f"Failed to fetch blog notes: {err}")

        transformed_notes = [transform_note(post) for post in posts]
        save_to_cache(transformed_notes)
        return transformed_notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blog notes: {e}")

@router.get("/notes/{slug}", response_model=BlogPost)
async def fetch_blog_post(slug: str):
    """
    Fetch a single blog post by its slug.
    
    Args:
        slug: URL-friendly identifier for the post
        api_key: Verified API key from header
        
    Returns:
        BlogPost: Single blog post matching the slug
        
    Raises:
        HTTPException: If post not found or API request fails
    """
    if cached_notes := get_from_cache():
        for post in cached_notes:
            if post.slug == slug:
                return post

    headers = {"Authorization": f"Bearer {os.getenv('HACKMD_API_KEY')}"}

    try:
        response = requests.get(f"{HACKMD_API_URL}/notes/{slug}", headers=headers)
        response.raise_for_status()
        post = response.json()
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blog post: {err}")

    return transform_note(post)

@router.post("/notes/refresh", response_model=List[BlogPost])
async def refresh_blog_notes():
    """
    Force refresh of blog notes cache.
    
    Args:
        api_key: Verified API key from header
    
    Returns:
        List[BlogPost]: Updated list of all blog notes
        
    Raises:
        HTTPException: If refresh operation fails
    """
    cache_path = Path("data/notes_cache.json")
    if cache_path.exists():
        cache_path.unlink()
    return await fetch_blog_notes()