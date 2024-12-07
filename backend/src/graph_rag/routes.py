from fastapi import APIRouter
from .models import PutBlobResult, Search

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "LightRAG API", "status": "running"}

@router.post("/create_graph/")
async def upload_files_api(data: PutBlobResult):
    """
    Process and index files using LightRAG.
    """
    from main import graph_rag_service  # Import the global instance
    print(data)
    return await graph_rag_service.create_graph(data)

@router.post("/search/")
async def search_api(data: Search):
    """
    Endpoint for performing semantic search using LightRAG.
    """
    from main import graph_rag_service  # Import the global instance
    return {
        "result": await graph_rag_service.run_query(
            query=data.text,
            method=data.method,
            community_level=data.community_level,
            response_type=data.response_type
        )
    } 