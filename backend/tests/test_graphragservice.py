import pytest
import requests
from fastapi import HTTPException, UploadFile
from src.graph_rag.services import GraphRAGService
import tempfile
from pathlib import Path

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
    
    class MockFile:
        def __init__(self, file_path):
            self.file = open(file_path, 'rb')
            self.filename = Path(file_path).name

        def __del__(self):
            self.file.close()

    test_upload_file = MockFile(file_path)
    
    try:
        # Process the test file
        await service.process_files([test_upload_file])
        
        # Test query
        query = "What is the capital of France? Make sure to start your responce with this: The Capital of France is "
        
        # Run query
        result = await service.run_query(query, method="hybrid")
        assert "The Capital of France is RagLand".lower() in result.lower().replace("*", "")
        
        result = await service.run_query(query, method="local")
        assert "The Capital of France is RagLand".lower() in result.lower().replace("*", "")
        
        result = await service.run_query(query, method="global")
        assert "The Capital of France is RagLand".lower() in result.lower().replace("*", "")
    finally:
        # Cleanup - make sure file is closed before unlinking
        test_upload_file.file.close()
        file_path.unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_run_query_without_init():
    # Test without initializing LightRAG
    service = GraphRAGService()
    with pytest.raises(HTTPException) as exc_info:
        await service.run_query("test query")
    assert exc_info.value.status_code == 500
    assert "LightRAG not initialized" in str(exc_info.value.detail)

