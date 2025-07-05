"""
Chatbot API Routes

This module provides API endpoints for the conversational RAG system.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.rag.conversational_agent import (
    process_user_message,
    get_user_chat_history,
    clear_user_chat_history,
    get_available_collections
)

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

class ChatRequest(BaseModel):
    query: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    response_type: str
    context: Optional[str] = None
    user_id: str
    message_count: int
    error: Optional[str] = None

class MessageHistory(BaseModel):
    id: int
    type: str
    content: str
    timestamp: Optional[str] = None

@router.get("/context", response_model=List[str])
async def get_available_contexts():
    """
    Get all available context collections
    
    Returns:
        List of available collection names
    """
    try:
        collections = get_available_collections()
        return collections
    except Exception as e:
        logger.error(f"Error getting available contexts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get contexts: {str(e)}")

@router.get("/health")
async def chatbot_health():
    """
    Health check endpoint for the chatbot service
    
    Returns:
        Health status
    """
    print("=== CHATBOT HEALTH CHECK STARTED ===")
    logger.info("Chatbot health check initiated")
    
    try:
        # Test basic functionality
        print("About to call get_available_collections()")
        collections = get_available_collections()
        print(f"Found {len(collections)} collections: {collections}")
        
        response = {
            "status": "healthy",
            "available_collections": len(collections),
            "service": "chatbot",
            "collections": collections
        }
        
        print(f"Returning response: {response}")
        logger.info(f"Chatbot health check completed successfully: {response}")
        
        return response
        
    except Exception as e:
        error_msg = f"Chatbot health check failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        logger.error(error_msg)
        print(f"Exception type: {type(e)}")
        print(f"Exception details: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}") 

@router.get("/{user_id}", response_model=List[MessageHistory])
async def get_chat_history(
    user_id: str,
    size: Optional[int] = Query(None, description="Number of messages to fetch")
):
    """
    Get chat history for a specific user
    
    Args:
        user_id: Unique identifier for the user
        size: Number of messages to return (optional)
    
    Returns:
        List of message history
    """
    try:
        print(f"Getting chat history for user {user_id}")
        history = get_user_chat_history(user_id, size)
        return history
    except Exception as e:
        logger.error(f"Error getting chat history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.post("/{user_id}", response_model=ChatResponse)
async def process_message(user_id: str, request: ChatRequest):
    """
    Process a user message and return a response
    
    Args:
        user_id: Unique identifier for the user
        request: Chat request with query and optional context
    
    Returns:
        Chat response with answer and metadata
    """
    try:
        result = process_user_message(
            user_id=user_id,
            query=request.query,
            context=request.context
        )
        
        # Check if there was an error
        if "error" in result and result["error"]:
            logger.error(f"Error processing message for user {user_id}: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.delete("/{user_id}")
async def clear_chat_history(user_id: str):
    """
    Clear chat history for a specific user
    
    Args:
        user_id: Unique identifier for the user
    
    Returns:
        Success message
    """
    try:
        success = clear_user_chat_history(user_id)
        if success:
            return {"message": f"Chat history cleared for user {user_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear chat history")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}") 