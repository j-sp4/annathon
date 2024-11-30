import os
import shutil
from pathlib import Path
from fastapi import HTTPException
from lightrag import LightRAG, QueryParam, EmbeddingFunc
from lightrag.llm import gpt_4o_mini_complete
from ..utils import logger

class GraphRAGService:
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        self.input_path = f"{base_path}/input"
        self.output_path = f"{base_path}/output"
        self.rag = None

    async def setup_directories(self):
        """Ensure required directories exist and initialize LightRAG"""
        os.makedirs(self.input_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)
        WORKING_DIR = "./local_neo4jWorkDir"
        
        # Initialize LightRAG
        self.rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=gpt_4o_mini_complete,  # You can change this to other models
            kg="Neo4JStorage"
        )

    async def run_query(self, query: str, method: str = "hybrid", community_level: int = 2, response_type: str = "Multiple Paragraphs"):
        """Run a LightRAG query"""
        try:
            if not self.rag:
                raise HTTPException(status_code=500, detail="LightRAG not initialized")
                
            # Convert method parameter to LightRAG query mode
            mode = {
                "global": "global",
                "local": "local",
                "hybrid": "hybrid",
                "naive": "naive"
            }.get(method, "hybrid")
            
            # Execute query
            result = self.rag.query(
                query,
                param=QueryParam(
                    mode=mode,
                    # Add any other relevant parameters here
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
                    self.rag.insert(content)
            
            return {"message": "Files processed successfully"}
            
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 