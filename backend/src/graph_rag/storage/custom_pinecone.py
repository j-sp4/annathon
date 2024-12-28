import asyncio
from dataclasses import dataclass
import os
from tqdm.asyncio import tqdm as tqdm_async
from pinecone import Pinecone
from lightrag.utils import logger
from lightrag.base import BaseVectorStorage


@dataclass
class PineconeVectorDBStorage(BaseVectorStorage):
    @staticmethod
    def create_index_if_not_exist(index_name: str, **kwargs):
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        if index_name in pc.list_indexes():
            return
        pc.create_index(
            name=index_name,
            metric="cosine",
            **kwargs
        )

    def __post_init__(self):
        # Initialize Pinecone first
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        self._max_batch_size = self.global_config["embedding_batch_num"]
        
        # Check if index exists before trying to create it
        existing_indexes = pc.list_indexes()
        if self.namespace not in existing_indexes:
            try:
                from pinecone import ServerlessSpec
                pc.create_index(
                    name=self.namespace,
                    dimension=self.embedding_func.embedding_dim,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            except Exception as e:
                # If index was created between our check and create attempt, that's okay
                if "ALREADY_EXISTS" not in str(e):
                    raise e
        
        # Only get the index after we're sure it exists
        self._index = pc.Index(self.namespace)

    async def upsert(self, data: dict[str, dict]):
        logger.info(f"Inserting {len(data)} vectors to {self.namespace}")
        if not len(data):
            logger.warning("You insert an empty data to vector DB")
            return []

        contents = [v["content"] for _, v in data.items()]
        batches = [
            contents[i : i + self._max_batch_size]
            for i in range(0, len(contents), self._max_batch_size)
        ]

        async def wrapped_task(batch):
            result = await self.embedding_func(batch)
            pbar.update(1)
            return result

        embedding_tasks = [wrapped_task(batch) for batch in batches]
        pbar = tqdm_async(
            total=len(embedding_tasks), desc="Generating embeddings", unit="batch"
        )
        embeddings_list = await asyncio.gather(*embedding_tasks)

        # Prepare vectors for Pinecone format
        vectors = []
        for i, (key, value) in enumerate(data.items()):
            metadata = {k: v for k, v in value.items() if k in self.meta_fields}
            vectors.append((
                key,
                embeddings_list[i // self._max_batch_size][i % self._max_batch_size].tolist(),
                metadata
            ))

        # Upsert in batches
        for i in range(0, len(vectors), self._max_batch_size):
            batch = vectors[i:i + self._max_batch_size]
            self._index.upsert(vectors=batch)

        return [v[0] for v in vectors]  # Return list of IDs

    async def query(self, query, top_k=5):
        embedding = await self.embedding_func([query])
        results = self._index.query(
            vector=embedding[0].tolist(),
            top_k=top_k,
            include_metadata=True
        )
        
        return [
            {
                **match.metadata,
                "id": match.id,
                "distance": 1 - match.score  # Convert cosine similarity to distance
            }
            for match in results.matches
        ]
