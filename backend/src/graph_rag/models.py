from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile

class UploadFiles(BaseModel):
    files: List[UploadFile]
    context: Optional[str] = None
    response: Optional[str] = None

class Search(BaseModel):
    text: str
    method: Optional[str] = "global"  # Can be "global" or "local"
    community_level: Optional[int] = 2
    response_type: Optional[str] = "Multiple Paragraphs"
