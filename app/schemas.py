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
from pydantic import BaseModel, validator

class DownloadRequest(BaseModel):
    url: str

class VideoFormat(BaseModel):
    quality: str
    url: str
    format_note: Optional[str]
    resolution: Optional[str]
    filesize: Optional[int]

class DownloadResponse(BaseModel):
    title: Optional[str]
    uploader: Optional[str]
    upload_date: Optional[str]
    description: Optional[str]
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    duration: Optional[int]  # Keep as int, but handle float conversion
    thumbnail: Optional[str]
    formats: List[VideoFormat]
    error: Optional[str] = None

    @validator('duration', pre=True)
    def convert_duration_to_int(cls, value):
        if isinstance(value, float):
            return int(value)  # Convert float to int (e.g., 18.481 -> 18)
        return value