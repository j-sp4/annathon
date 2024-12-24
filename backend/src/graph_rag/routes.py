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

@router.get("/search")
async def search_api(q: str):
    """
    Endpoint for performing semantic search using LightRAG.
    Query params:
    - q: search query text
    - method: search method (default: "hybrid")
    - community_level: community level (default: 1)
    - response_type: response type (default: "text")
    """
    from main import graph_rag_service  # Import the global instance
    return {
        "result": await graph_rag_service.run_query(
            query=q,
        )
    } 