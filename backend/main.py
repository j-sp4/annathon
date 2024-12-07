from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.graph_rag import router as graph_rag_router
from src.graph_rag.services import GraphRAGService

app = FastAPI()
graph_rag_service = None  # Global variable to store the service instance

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GraphRAG service


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    global graph_rag_service
    graph_rag_service = GraphRAGService()
    await graph_rag_service.setup_directories()

# Include GraphRAG routes
app.include_router(graph_rag_router, prefix="/api/v1")






