import os
import sys
from pathlib import Path
import pytest
# Add backend directory to Python path
backend_path = str(Path(__file__).parent.parent)
sys.path.append(backend_path)

from src.graph_rag.services import GraphRAGService



@pytest.fixture(autouse=True)
def setup_test_env():
    """Fixture to set up test-specific environment variables."""
    # Store original env vars (if they exist)
    NEO4J_AUTH = os.environ.get('NEO4J_AUTH')
    if not NEO4J_AUTH:
        raise ValueError("NEO4J_AUTH is not set")

    # Set test-specific env vars
    NEO4J_USERNAME, NEO4J_PASSWORD = NEO4J_AUTH.split('/')
    NEO4J_URI="neo4j://localhost:7687"
    os.environ['NEO4J_URI'] = NEO4J_URI
    os.environ['NEO4J_USERNAME'] = NEO4J_USERNAME
    os.environ['NEO4J_PASSWORD'] = NEO4J_PASSWORD
      # Run the test

    # Cleanup can be added here if needed
    # await cleanup_resources()
