import os
import shutil
from pathlib import Path
from fastapi import HTTPException
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete
from ..utils.logger import logger
from .storage.custom_neo4j import CustomNeo4JStorage
from .storage.custom_pinecone import PineconeVectorDBStorage
from lightrag.lightrag import LightRAG
from .models import PutBlobResult
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List

# Patch the storage class registry
def setup_custom_storage():
    # Get the original storage classes
    original_storage_classes = LightRAG._get_storage_class(None)
    
    # Add our custom storage classes to the existing dictionary
    original_storage_classes.update({
        "CustomNeo4JStorage": CustomNeo4JStorage,
        "CustomPineconeVectorDBStorage": PineconeVectorDBStorage,
    })

    print(original_storage_classes)
    
    # Monkey patch the _get_storage_class method
    def new_get_storage_class(self):
        return original_storage_classes
    
    LightRAG._get_storage_class = new_get_storage_class
    return original_storage_classes

class GraphRAGService:
    def __init__(self, base_path: str = "./data", working_dir: str = "./local_neo4jWorkDir"):
        self.base_path = base_path
        self.input_path = f"{base_path}/input"
        self.output_path = f"{base_path}/output"
        self.rag = None
        self.working_dir = working_dir

    setup_custom_storage()
    
    async def setup_directories(self):
        """Ensure required directories exist and initialize LightRAG"""
        try:
            # Create directories with explicit permissions
            os.makedirs(self.working_dir, mode=0o777, exist_ok=True)
            
            logger.info(f"Created directories: {self.input_path}, {self.output_path}, {self.working_dir}")

            # NEO4J_AUTH = os.environ.get('NEO4J_AUTH')
            # NEO4J_USERNAME, NEO4J_PASSWORD = NEO4J_AUTH.split('/')
            
            # Initialize LightRAG with correct parameters
            self.rag = LightRAG(
                working_dir=self.working_dir,
                graph_storage="CustomNeo4JStorage",
                log_level="DEBUG",
                vector_storage="CustomPineconeVectorDBStorage",
                kv_storage="MongoKVStorage",
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

    async def create_graph(self, data: PutBlobResult):
        """Process multiple uploaded files with LightRAG"""
        try:
            if not self.rag:
                logger.error("LightRAG not initialized")
                logger.error(self.rag)
                raise HTTPException(status_code=500, detail="LightRAG not initialized")
            
            @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
            async def fetch_url(client: httpx.AsyncClient, url: str) -> str:
                logger.info(f"Fetching content from: {url}")
                if url.startswith('file://'):
                    file_path = url[7:]
                    logger.info(f"Reading local file: {file_path}")
                    with open(file_path, 'r') as f:
                        return f.read()
                else:
                    timeout = httpx.Timeout(30.0, connect=10.0)  # 30s total timeout, 10s connect timeout
                    response = await client.get(url, timeout=timeout)
                    response.raise_for_status()
                    return response.text

            async def process_url(url: str) -> str:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        return await fetch_url(client, url)
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {str(e)}")
                    raise

            # Process URLs in smaller batches to avoid overwhelming the system
            batch_size = 5
            all_contents: List[str] = []
            
            for i in range(0, len(data.urls), batch_size):
                batch_urls = data.urls[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} with {len(batch_urls)} URLs")
                
                try:
                    batch_contents = await asyncio.gather(
                        *[process_url(url) for url in batch_urls],
                        return_exceptions=True
                    )
                    
                    # Filter out any errors and log them
                    for url, content in zip(batch_urls, batch_contents):
                        if isinstance(content, Exception):
                            logger.error(f"Failed to process {url}: {str(content)}")
                        else:
                            all_contents.append(content)
                
                except Exception as e:
                    logger.error(f"Batch processing error: {str(e)}")
                    continue

            # Insert successful contents into RAG
            success_count = 0
            for content in all_contents:
                try:
                    await self.rag.ainsert(content)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error inserting content into RAG: {str(e)}")

            if success_count == 0:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to process any files successfully"
                )

            return {
                "message": f"Successfully processed {success_count} out of {len(data.urls)} files",
                "failed": len(data.urls) - success_count
            }
            
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 