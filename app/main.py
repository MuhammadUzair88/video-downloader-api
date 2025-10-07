# from typing import List
# from fastapi import FastAPI, Depends, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import yt_dlp

# from .dependencies import get_api_key
# from .schemas import DownloadRequest, DownloadResponse, VideoFormat

# app = FastAPI(
#     title="Video Downloader API",
#     description="A REST API for downloading videos from various social media platforms using yt-dlp, with metadata extraction.",
#     version="1.1.0"
# )

# # Configure CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",  # Frontend dev server
#         # Add your production frontend URL, e.g., "https://your-frontend-domain.com"
#     ],
#     allow_credentials=True,
#     allow_methods=["POST", "GET"],  # Restrict to needed methods
#     allow_headers=["Content-Type", "X-API-Key"],  # Restrict to needed headers
# )

# @app.post("/api/v1/download", response_model=DownloadResponse, dependencies=[Depends(get_api_key)])
# async def download_video(request: DownloadRequest):
#     """
#     Endpoint to get downloadable video links and metadata from a given URL.
    
#     - **url**: The video URL from supported platforms.
    
#     Returns downloadable links for available formats (prioritizing video formats) plus extended metadata.
#     """
#     ydl_opts = {
#         'quiet': True,
#         'no_warnings': True,
#         'format': 'bestvideo+bestaudio/best',  # Extract info without downloading
#     }
    
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(request.url, download=False)
            
#             # Extract relevant info
#             title = info.get('title')
#             uploader = info.get('uploader')
#             upload_date = info.get('upload_date')
#             description = info.get('description')
#             view_count = info.get('view_count')
#             like_count = info.get('like_count')
#             comment_count = info.get('comment_count')
#             thumbnail = info.get('thumbnail')
#             duration = info.get('duration')
            
#             # Get formats, filter for video/audio
#             formats = []
#             for f in info.get('formats', []):
#                 if f.get('vcodec') != 'none' or f.get('acodec') != 'none':  # Video or audio formats
#                     quality = "Audio" if f.get('vcodec') == 'none' else (
#                         "HD" if f.get('height', 0) >= 720 else "SD"
#                     )
#                     formats.append(VideoFormat(
#                         quality=quality,
#                         url=f['url'],
#                         format_note=f.get('format_note'),
#                         resolution=f.get('resolution'),
#                         filesize=f.get('filesize')
#                     ))
            
#             # Sort formats: HD first, then SD, then Audio
#             formats.sort(key=lambda x: (x.quality == "HD", x.quality == "SD", x.quality == "Audio"), reverse=True)
            
#             return DownloadResponse(
#                 title=title,
#                 uploader=uploader,
#                 upload_date=upload_date,
#                 description=description,
#                 view_count=view_count,
#                 like_count=like_count,
#                 comment_count=comment_count,
#                 duration=duration,
#                 thumbnail=thumbnail,
#                 formats=formats,
#                 error=None
#             )
    
#     except yt_dlp.utils.DownloadError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal server error: " + str(e))




from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import yt_dlp
import aiohttp
import os
import tempfile
import time # Import time module for cache TTL

from .dependencies import get_api_key
from .schemas import DownloadRequest, DownloadResponse, VideoFormat

app = FastAPI(
    title="Video Downloader API",
    description="A REST API for downloading videos from various social media platforms using yt-dlp, with metadata extraction.",
    version="1.1.1"
)

# In-memory cache for yt-dlp results
video_cache = {}
CACHE_TTL = 3600 # Cache Time-To-Live in seconds (1 hour)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.post("/api/v1/download", response_model=DownloadResponse, dependencies=[Depends(get_api_key)])
async def download_video(request: DownloadRequest):
    """
    Extract video metadata and formats from supported platforms.
    """
    # Check cache first
    if request.url in video_cache:
        cached_data, timestamp = video_cache[request.url]
        if time.time() - timestamp < CACHE_TTL:
            return cached_data

    # 🔒 Option 1: Use cookies.txt file (included in repo)
    cookie_file_path = os.path.join(os.path.dirname(__file__), "cookies.txt")

    # 🔒 Option 2: Use environment variable (safer)
    if not os.path.exists(cookie_file_path):
        cookies_env = os.getenv("INSTAGRAM_COOKIES")
        if cookies_env:
            temp_cookie = tempfile.NamedTemporaryFile(delete=False)
            temp_cookie.write(cookies_env.encode('utf-8'))
            temp_cookie.flush()
            cookie_file_path = temp_cookie.name

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo+bestaudio/best',
        'extract_flat': True,
        'force_generic_extractor': False,
    }

    if os.path.exists(cookie_file_path):
        ydl_opts['cookiefile'] = cookie_file_path

    temp_cookie_file_created = False
    if cookies_env and not os.path.exists(os.path.join(os.path.dirname(__file__), "cookies.txt")):
        temp_cookie_file_created = True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)

            # Extract metadata safely
            title = info.get('title')
            uploader = info.get('uploader')
            upload_date = info.get('upload_date')
            description = info.get('description')
            view_count = int(info.get('view_count')) if info.get('view_count') else None
            like_count = int(info.get('like_count')) if info.get('like_count') else None
            comment_count = int(info.get('comment_count')) if info.get('comment_count') else None
            thumbnail = info.get('thumbnail')
            duration = info.get('duration')

            # Build formats list
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                    quality = "Audio" if f.get('vcodec') == 'none' else (
                        "HD" if f.get('height', 0) >= 720 else "SD"
                    )
                    formats.append(VideoFormat(
                        quality=quality,
                        url=f['url'],
                        format_note=f.get('format_note'),
                        resolution=f.get('resolution'),
                        filesize=int(f.get('filesize')) if f.get('filesize') else None
                    ))

            formats.sort(
                key=lambda x: (x.quality == "HD", x.quality == "SD", x.quality == "Audio"),
                reverse=True
            )

            response = DownloadResponse(
                title=title,
                uploader=uploader,
                upload_date=upload_date,
                description=description,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                duration=duration,
                thumbnail=thumbnail,
                formats=formats,
                error=None
            )

            # Store in cache
            video_cache[request.url] = (response, time.time())
            return response

    except yt_dlp.utils.DownloadError as e:
        return DownloadResponse(error=str(e), formats=[])
    except Exception as e:
        return DownloadResponse(error="Internal server error: " + str(e), formats=[])
    finally:
        if temp_cookie_file_created and os.path.exists(cookie_file_path):
            os.remove(cookie_file_path)


@app.get("/api/v1/proxy-video")
async def proxy_video(url: str):
    """
    Proxy endpoint to stream video content, bypassing CORS.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch video stream")
            headers = {
                "Content-Type": resp.headers.get("Content-Type", "video/mp4"),
                "Access-Control-Allow-Origin": "*",
            }
            return StreamingResponse(resp.content, headers=headers)
