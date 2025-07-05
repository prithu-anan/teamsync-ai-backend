"""
Embedding Model Configuration for RAG System

This module provides a centralized configuration for embedding models used in the RAG system.
Supports both OpenAI and HuggingFace embeddings with easy selection.
"""

import os
from typing import Union
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedding_model(
    model_type: str = "openai",
    model_name: str = "text-embedding-3-small"
) -> Union[OpenAIEmbeddings, HuggingFaceEmbeddings]:
    """
    Get a configured embedding model instance.
    
    Args:
        model_type: Type of embedding model ("openai" or "huggingface")
        model_name: Specific model name/identifier
    
    Returns:
        Configured embedding model instance
    
    Raises:
        ValueError: If model_type is not supported
    """
    if model_type.lower() == "openai":
        return OpenAIEmbeddings(
            model=model_name,
            timeout=30
        )
    elif model_type.lower() == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=model_name
        )
    else:
        raise ValueError(f"Unsupported model_type: {model_type}. Supported types: 'openai', 'huggingface'")

# Default embedding model instance for easy import
# Using OpenAI text-embedding-3-small as default
embedding_model = get_embedding_model("openai", "text-embedding-3-small") 