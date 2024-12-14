"""
TODO:
"""

import os
import tempfile
from loguru import logger

import nest_asyncio  # from: https://github.com/HKUDS/LightRAG/issues/15

nest_asyncio.apply()
from lightrag import LightRAG
from lightrag.llm import (
    hf_model_complete,
    hf_embedding,
    ollama_model_complete,
    ollama_embedding,
)
from transformers import AutoModel, AutoTokenizer
from lightrag.utils import EmbeddingFunc


class Benchmarker:
    """
    TODO:
    """

    def __init__(
        self,
        filepath_results: str = "benchmark_results.txt",
        dir_benchmarking: str = "./benchmarking",
        configs: tuple[tuple[str, str, int, str], ...] = (
            (
                "hf",
                "internlm/internlm2-chat-1_8b",
                384,
                "sentence-transformers/all-MiniLM-L6-v2",
            )
        ),
    ):
        """
        TODO:
        """

        self.filepath_results = filepath_results
        self.dir_benchmarking = dir_benchmarking
        self.dir_working = None
        self.configs = configs

        self.graph_storage = "Neo4JStorage"
        self.log_level = "DEBUG"

    # def create_working_directory(self):
    #     """
    #     TODO:
    #     """
    #     if not os.path.exists(self.dir_working):
    #         os.mkdir(self.dir_working)

    def create_benchmarking_directory(self):
        """
        TODO:
        """
        if not os.path.exists(self.dir_benchmarking):
            os.mkdir(self.dir_benchmarking)

    def setup(self, config: tuple) -> LightRAG:
        """
        TODO:
        config: (model_repo, embedding_dim, embedding_repo)
        """

        if config[0] == "gpt":
            rag = LightRAG(
                working_dir=self.dir_working,
                llm_model_func=config[1],
                graph_storage=self.graph_storage,  # <-----------override KG default
                log_level=self.log_level,  # <-----------override log_level default
            )

            return rag
        if config[0] == "hf":
            rag = LightRAG(
                working_dir=self.dir_working,
                graph_storage=self.graph_storage,  # <-----------override KG default
                log_level=self.log_level,  # <-----------override log_level default
                llm_model_func=hf_model_complete,
                llm_model_name=config[1],
                embedding_func=EmbeddingFunc(
                    embedding_dim=config[2],
                    max_token_size=5000,
                    func=lambda texts: hf_embedding(
                        texts,
                        tokenizer=AutoTokenizer.from_pretrained(config[3]),
                        embed_model=AutoModel.from_pretrained(config[3]),
                    ),
                ),
            )

            return rag
        if config[0] == "ollama":

            rag = LightRAG(
                working_dir=self.dir_working,
                graph_storage=self.graph_storage,  # <-----------override KG default
                log_level=self.log_level,  # <-----------override log_level default
                llm_model_func=ollama_model_complete,
                llm_model_name=config[1],
                embedding_func=EmbeddingFunc(
                    embedding_dim=config[2],
                    max_token_size=8192,
                    func=lambda texts: ollama_embedding(texts, embed_model=config[3]),
                ),
            )

            return rag

        raise NotImplementedError

    def teardown(self, rag):
        """
        TODO:
        """
        del rag

    def run(self, benchmarks: list):
        """
        TODO:
        """

        for this_benchmark in benchmarks:
            for this_config in self.configs:
                with tempfile.TemporaryDirectory(self.dir_benchmarking) as tempdir:
                    self.dir_working = tempdir
                    rag = self.setup(this_config)
                    this_benchmark(rag)
                    self.teardown(rag)

    def benchmark1(self, rag):
        """
        TODO:
        """
        logger.info("Running Benchmark1 ...")

    def benchmark2(self, rag):
        """
        TODO:
        """
        logger.info("Running Benchmark2 ...")

    def benchmark3(self, rag):
        """
        TODO:
        """
        logger.info("Running Benchmark3 ...")
