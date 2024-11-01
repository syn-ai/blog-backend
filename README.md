## HackMD Blog API

A FastAPI backend service that interfaces with the HackMD API to fetch and cache blog posts, with robust static file management.

### Features

- Fetch all blog posts from HackMD
- Fetch individual blog posts by slug
- Local caching system for improved performance
- Force cache refresh endpoint
- Type-safe responses using Pydantic models
- Static file management with automatic backups
- JSON file handling with error management
- File listing and filtering capabilities

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- HackMD API key

### Installation

1. Clone the repository:

```
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:

```
pip install fastapi uvicorn requests python-dotenv pydantic
```

3. Create a .env file in the root directory:

```
HACKMD_API_KEY=your_hackmd_api_key_here
```

Project Structure
```
.
├── main.py # FastAPI application entry point
├── src/
│ └── blog_posts/
│ └── hackmd.py # Blog post retrieval and caching logic
├── data/
│ └── posts_cache.json # Cache storage (created automatically)
│ └── backups/ # Backup directory for static files
└── README.md
```

### API Endpoints

**GET `/posts`**

Fetches all blog posts. Returns cached data if available, otherwise fetches from HackMD API.

Response format:

```
[
{
"id": "string",
"title": "string",
"content": "string",
"publishDate": "string",
"lastModified": "string",
"excerpt": "string",
"slug": "string",
"coverImage": "string | null",
"readingTime": "string | null"
}
]
```

**GET `/posts/{slug}`**

Fetches a single blog post by slug.

Response format: Same as single post object above.

**POST `/posts/refresh`**

Forces a refresh of the blog posts cache.

Response format: Array of updated blog posts.

### Static file management

**GET `/api/files`**

Lists all files in the static directory. Can be filtered by extension.

**POST `/api/backup/{filename}`**

Creates a timestamped backup of a specific file.

**GET `/api/backups`**

Lists all available backups. Can be filtered by original filename.

### Running the Server

Start the development server:

```
uvicorn main:app --host 0.0.0.0 --port 4050 --reload
```
The API will be available at `http://localhost:4050`

### API Documentation

FastAPI automatically generates API documentation. After starting the server, visit:

Swagger UI: `http://localhost:4050/docs`
ReDoc: `http://localhost:4050/redoc`

### Static File Management

The service includes a robust static file management system:

- Automatic directory creation and management
- JSON file handling with proper error management
- Timestamped backup system
- File listing and filtering capabilities
- Safe file operations with automatic backups
- Backup restoration functionality

### Key Features:

- Create and manage backups automatically
- List files with optional extension filtering
- Safe file deletion with automatic backup creation
- JSON file validation and error handling
- Backup restoration capabilities

### Cache Management

The service implements a simple file-based caching system:

- Cache location: `data/posts_cache.json`
- Cache is automatically created on first API call
- Cache can be manually refreshed using the `/posts/refresh` endpoint
- Cache is updated whenever new data is fetched from HackMD

### Error Handling

The API implements proper error handling for:

- Failed API requests to HackMD
- Invalid slugs
- Missing API keys
- Cache read/write errors
- File system operations
- JSON parsing and validation

All errors return appropriate HTTP status codes and descriptive error messages.

### Environment Variables

```
| Variable       | Description         | Required |
|----------------|---------------------|----------|
| HACKMD_API_KEY | Your HackMD API key | Yes      | 
```

### Contributing

1. Fork the repository

2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request.

### License

This project is licensed under the MIT License - see the LICENSE file for details.