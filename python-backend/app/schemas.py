# from typing import List, Optional
# from pydantic import BaseModel

# class DownloadRequest(BaseModel):
#     url: str

# class VideoFormat(BaseModel):
#     quality: str
#     url: str
#     format_note: Optional[str]
#     resolution: Optional[str]
#     filesize: Optional[int]

# class DownloadResponse(BaseModel):
#     title: Optional[str]
#     uploader: Optional[str]
#     upload_date: Optional[str]
#     description: Optional[str]
#     view_count: Optional[int]
#     like_count: Optional[int]
#     comment_count: Optional[int]
#     duration: Optional[int]
#     thumbnail: Optional[str]
#     formats: List[VideoFormat]
#     error: Optional[str]  # Should already be Optional[str]



from typing import List, Optional
from pydantic import BaseModel

class VideoFormat(BaseModel):
    quality: str
    url: str
    format_note: Optional[str]
    resolution: Optional[str]
    filesize: Optional[int]

class DownloadRequest(BaseModel):
    url: str

class DownloadResponse(BaseModel):
    title: Optional[str]
    uploader: Optional[str]
    upload_date: Optional[str]
    description: Optional[str]
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    duration: Optional[int]
    thumbnail: Optional[str]
    formats: List[VideoFormat]
    error: Optional[str]
