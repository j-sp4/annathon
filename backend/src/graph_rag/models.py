from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile

class UploadFiles(BaseModel):
    files: List[UploadFile]
    context: Optional[str] = None
    response: Optional[str] = None

class Search(BaseModel):
    text: str
    method: Optional[str] = "hybrid"  # Can be "hybrid", "global", "local", or "naive"
    community_level: Optional[int] = 2  # Kept for backward compatibility
    response_type: Optional[str] = "Multiple Paragraphs"  # Kept for backward compatibility

class PutBlobResult(BaseModel):
    urls: list[str]
    download_urls: list[str]
    pathnames: list[str]
    content_types: list[str | None] = None
    content_dispositions: list[str]