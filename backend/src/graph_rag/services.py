import os
import shutil
import asyncio
from pathlib import Path
from fastapi import HTTPException
from loguru import logger

class GraphRAGService:
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        self.input_path = f"{base_path}/input"
        self.output_path = f"{base_path}/output"

    async def setup_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.input_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)

    async def run_indexing_pipeline(self):
        """Run the GraphRAG indexing pipeline"""
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "graphrag.index",
                "--root", self.base_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Indexing pipeline failed: {stderr.decode()}")
                raise HTTPException(status_code=500, detail="Indexing pipeline failed")
                
            return True
        except Exception as e:
            logger.error(f"Error running indexing pipeline: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to run indexing pipeline")

    async def run_query(self, query: str, method: str, community_level: int, response_type: str):
        """Run a GraphRAG query"""
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "graphrag.query",
                "--root", self.base_path,
                "--method", method,
                "--community_level", str(community_level),
                "--response_type", response_type,
                query,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Query failed: {stderr.decode()}")
                raise HTTPException(status_code=500, detail="Query execution failed")
                
            return stdout.decode().strip()
        except Exception as e:
            logger.error(f"Error running query: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to execute query")

    async def process_files(self, files):
        """Process uploaded files"""
        try:
            # Clear input directory
            shutil.rmtree(self.input_path, ignore_errors=True)
            os.makedirs(self.input_path)
            
            # Save uploaded files
            for file in files:
                file_path = Path(self.input_path) / file.filename
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
            
            # Run indexing pipeline
            await self.run_indexing_pipeline()
            
            return {"message": "Files processed successfully"}
            
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 