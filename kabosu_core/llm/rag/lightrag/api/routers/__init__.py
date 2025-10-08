"""
This module contains all the routers for the LightRAG API.
"""

from kabosu_core.llm.rag.lightrag.api.routers.document_routes import router as document_router
from kabosu_core.llm.rag.lightrag.api.routers.query_routes import router as query_router
from kabosu_core.llm.rag.lightrag.api.routers.graph_routes import router as graph_router
from kabosu_core.llm.rag.lightrag.api.routers.ollama_api import OllamaAPI

__all__ = ["document_router", "query_router", "graph_router", "OllamaAPI"]
