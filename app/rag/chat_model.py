"""
Chat Model Configuration for RAG System

This module provides a centralized configuration for the LLM model used in the RAG system.
Currently configured to use Google's Gemini model, but can be easily extended to support
other providers like OpenAI, Anthropic, etc.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

def get_chat_model(
    model_name: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 1000,
    top_p: float = 1.0,
    top_k: int = 40
) -> ChatGoogleGenerativeAI:
    """
    Get a configured chat model instance.
    
    Args:
        model_name: The model to use (default: gemini-2.0-flash)
        temperature: Controls randomness in responses (0.0 = deterministic)
        max_tokens: Maximum number of tokens in response
        top_p: Nucleus sampling parameter
        top_k: Top-k sampling parameter
    
    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    return ChatGoogleGenerativeAI(
        model=model_name,
        client_options=None,
        transport=None,
        additional_headers=None,
        client=None,
        api_key=SecretStr(os.getenv("GEMINI_API_KEY") or "") if os.getenv("GEMINI_API_KEY") else None,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        top_k=top_k
    )

# Default model instance for easy import
model = get_chat_model() 