import os
import shutil
from pathlib import Path
from fastapi import HTTPException
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete
from ..utils.logger import logger
from .storage.custom_neo4j import CustomNeo4JStorage
from lightrag.lightrag import LightRAG

# Patch the storage class registry
def setup_custom_storage():
    # Access the storage class dictionary directly
    storage_classes = {
        # Keep existing storage classes
        "JsonKVStorage": LightRAG._get_storage_class(None)["JsonKVStorage"],
        "NanoVectorDBStorage": LightRAG._get_storage_class(None)["NanoVectorDBStorage"],
        "NetworkXStorage": LightRAG._get_storage_class(None)["NetworkXStorage"],
        # Add our custom storage
        "CustomNeo4JStorage": CustomNeo4JStorage
    }
    
    # Monkey patch the _get_storage_class method
    def new_get_storage_class(self):
        return storage_classes
    
    LightRAG._get_storage_class = new_get_storage_class
    return storage_classes

class GraphRAGService:
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        self.input_path = f"{base_path}/input"
        self.output_path = f"{base_path}/output"
        self.rag = None
        self.working_dir = "./local_neo4jWorkDir"

    setup_custom_storage()
    
    async def setup_directories(self):
        """Ensure required directories exist and initialize LightRAG"""
        try:
            # Create directories with explicit permissions
            os.makedirs(self.working_dir, mode=0o777, exist_ok=True)
            
            logger.info(f"Created directories: {self.input_path}, {self.output_path}, {self.working_dir}")

            NEO4J_AUTH = os.environ.get('NEO4J_AUTH')
            NEO4J_USERNAME, NEO4J_PASSWORD = NEO4J_AUTH.split('/')
            
            # Initialize LightRAG with correct parameters
            self.rag = LightRAG(
            working_dir=self.working_dir,
            graph_storage="CustomNeo4JStorage",
            log_level="DEBUG"
            )
            logger.info("LightRAG initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup directories or initialize LightRAG: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize: {str(e)}"
            )

    async def run_query(self, query: str, method: str = "hybrid", community_level: int = 2, response_type: str = "Multiple Paragraphs"):
        """Run a LightRAG query"""
        try:
            if not self.rag:
                raise HTTPException(status_code=500, detail="LightRAG not initialized")
                
            mode = {
                "global": "global",
                "local": "local",
                "hybrid": "hybrid",
                "naive": "naive"
            }.get(method, "hybrid")
            
            result = await self.rag.aquery(
                query,
                param=QueryParam(
                    mode=mode,
                )
            )
                
            return result
            
        except Exception as e:
            logger.error(f"Error running query: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")

    async def process_files(self, files):
        """Process uploaded files with LightRAG"""
        try:
            if not self.rag:
                raise HTTPException(status_code=500, detail="LightRAG not initialized")

            # Clear input directory
            shutil.rmtree(self.input_path, ignore_errors=True)
            os.makedirs(self.input_path)
            
            # Process each file
            for file in files:
                file_path = Path(self.input_path) / file.filename
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                
                # Read and insert content into LightRAG
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    await self.rag.ainsert(content)
            
            return {"message": "Files processed successfully"}
            
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 