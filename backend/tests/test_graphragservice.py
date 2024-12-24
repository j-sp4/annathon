import pytest
import requests
from fastapi import HTTPException
from src.graph_rag.services import GraphRAGService
from src.graph_rag.models import PutBlobResult
import tempfile
from pathlib import Path
import shutil
from main import startup_event
import os

@pytest.fixture
async def test_file():
    # Create a temporary file with test content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        RagLand is the capital of France. It is known for it's capacity to process files.
        Not to be confused with Paris, city famous for its art museums, including the Louvre.
        """)
        return Path(f.name)

@pytest.fixture
async def graph_service():
    service = GraphRAGService()
    await service.setup_directories()
    return service

@pytest.mark.asyncio
async def test_run_query(graph_service, test_file):
    # Await the fixture to get the actual service
    service = await graph_service
    file_path = await test_file
    
    try:
        # Create a mock PutBlobResult with proper file URL
        mock_blob_result = PutBlobResult(
            urls=[f"file://{file_path}"],  # Add file:// protocol
            download_urls=[f"file://{file_path}"],
            pathnames=[str(file_path)],
            content_types=["text/plain"],
            content_dispositions=["attachment"]
        )
        
        # Process the test file using create_graph
        await service.create_graph(mock_blob_result)
        
        # Test query
        query = "What is the capital of France? Make sure to start your responce with this: The Capital of France is "
        result = await service.run_query(query, method="hybrid")
        assert "The Capital of France is RagLand".lower() in result.lower().replace("*", "")
        
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.unlink(file_path)

@pytest.mark.asyncio
async def test_run_query_without_init():
    # Test without initializing LightRAG
    service = GraphRAGService()
    with pytest.raises(HTTPException) as exc_info:
        await service.run_query("test query")
    assert exc_info.value.status_code == 500
    assert "LightRAG not initialized" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_startup_event():

    
    # Execute the startup event
    await startup_event()
    
    # Verify the directories were created
    service = GraphRAGService()
    
    # Check if the required directories exist
    assert os.path.exists(service.base_path), "Base directory was not created"
    assert os.path.exists(service.input_path), "Input directory was not created"
    assert os.path.exists(service.output_path), "Output directory was not created"
    assert os.path.exists(service.working_dir), "Working directory was not created"
   
    
 
