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

from .dependencies import get_api_key
from .schemas import DownloadRequest, DownloadResponse, VideoFormat

app = FastAPI(
    title="Video Downloader API",
    description="A REST API for downloading videos from various social media platforms using yt-dlp, with metadata extraction.",
    version="1.1.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        # Add your production frontend URL, e.g., "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "X-API-Key"],
)

@app.post("/api/v1/download", response_model=DownloadResponse, dependencies=[Depends(get_api_key)])
async def download_video(request: DownloadRequest):
    """
    Endpoint to get downloadable video links and metadata from a given URL.
    
    - **url**: The video URL from supported platforms.
    
    Returns downloadable links for available formats (prioritizing video formats) plus extended metadata.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo+bestaudio/best',  # Prioritize best quality
        'extract_flat': True,  # Avoid downloading, get metadata
        'force_generic_extractor': False,  # Allow platform-specific extractors
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            # Extract relevant info with type safety
            title = info.get('title')
            uploader = info.get('uploader')
            upload_date = info.get('upload_date')
            description = info.get('description')
            view_count = int(info.get('view_count')) if info.get('view_count') else None
            like_count = int(info.get('like_count')) if info.get('like_count') else None
            comment_count = int(info.get('comment_count')) if info.get('comment_count') else None
            thumbnail = info.get('thumbnail')
            duration = info.get('duration')  # Validator will handle float-to-int conversion
            
            # Get formats, filter for video/audio
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
            
            # Sort formats: HD first, then SD, then Audio
            formats.sort(key=lambda x: (x.quality == "HD", x.quality == "SD", x.quality == "Audio"), reverse=True)
            
            return DownloadResponse(
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
    
    except yt_dlp.utils.DownloadError as e:
        return DownloadResponse(
            title=None,
            uploader=None,
            upload_date=None,
            description=None,
            view_count=None,
            like_count=None,
            comment_count=None,
            duration=None,
            thumbnail=None,
            formats=[],
            error=str(e)
        )
    except Exception as e:
        return DownloadResponse(
            title=None,
            uploader=None,
            upload_date=None,
            description=None,
            view_count=None,
            like_count=None,
            comment_count=None,
            duration=None,
            thumbnail=None,
            formats=[],
            error="Internal server error: " + str(e)
        )

@app.get("/api/v1/proxy-video")
async def proxy_video(url: str):
    """
    Proxy endpoint to stream video content, bypassing CORS restrictions.
    
    - **url**: The video URL to proxy.
    
    Returns a streaming response with CORS headers.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch video stream")
            headers = {
                "Content-Type": resp.headers.get("Content-Type", "video/mp4"),
                "Access-Control-Allow-Origin": "http://localhost:5173",
                # Add production frontend URL if needed
            }
            return StreamingResponse(resp.content, headers=headers)