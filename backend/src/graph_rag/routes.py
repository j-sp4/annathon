from fastapi import APIRouter
from .models import UploadFiles, Search
from .services import GraphRAGService

router = APIRouter()
graph_rag_service = GraphRAGService()

@router.get("/")
async def root():
    return {"message": "LightRAG API", "status": "running"}

@router.post("/upload_files/")
async def upload_files_api(data: UploadFiles):
    """
    Process and index files using LightRAG.
    """
    return await graph_rag_service.process_files(data.files)

@router.post("/search/")
async def search_api(data: Search):
    """
    Endpoint for performing semantic search using LightRAG.
    """
    return {
        "result": await graph_rag_service.run_query(
            query=data.text,
            method=data.method,
            community_level=data.community_level,
            response_type=data.response_type
        )
    } 