"""
Conversational Agent for RAG System

This module provides functionality for conversational AI with context-aware responses.
It supports user-specific chat history and can work with or without RAG context.
"""

import os
from typing import List, Optional, Dict, Any
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Qdrant
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory

from app.rag.quadrant_client import qdrant_client
from app.rag.chat_model import model
from app.rag.embedding_model import embedding_model

# === Firebase/Firestore setup ===
PROJECT_ID = os.getenv("PROJECT_ID")
CHAT_HISTORY_COLLECTION = "rag_chat_history"

# Initialize Firestore client
firestore_client = firestore.Client(project=PROJECT_ID)

def get_chat_history(user_id: str) -> FirestoreChatMessageHistory:
    """Get Firebase chat history for a specific user"""
    return FirestoreChatMessageHistory(
        session_id=user_id,
        collection=CHAT_HISTORY_COLLECTION,
        client=firestore_client,
    )

def get_rag_chain(collection_name: str):
    """Create a RAG chain for a specific collection"""
    
    # Create a retriever for the collection
    qdrant_store = Qdrant(
        client=qdrant_client,
        collection_name=collection_name,
        embeddings=embedding_model,
    )
    
    retriever = qdrant_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )
    
    # Enhanced contextualize question prompt
    contextualize_q_system_prompt = (
        "You are an expert at reformulating questions to be more specific and searchable. "
        "Given a chat history and the latest user question which might reference context "
        "in the chat history, formulate a standalone question which can be understood "
        "without the chat history. "
        "\n\nGuidelines:"
        "\n- If the question is already standalone, return it as is"
        "\n- If it references previous context, make it explicit"
        "\n- Focus on the core information being requested"
        "\n- Use clear, specific language"
        "\n- Do NOT answer the question, just reformulate it"
        "\n- If the question is about a person, include their name explicitly"
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # Create a history-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )
    
    # Enhanced answer question prompt
    qa_system_prompt = (
        "You are a knowledgeable assistant with access to detailed information. "
        "Use the following pieces of retrieved context to answer the question comprehensively and accurately."
        "\n\nGuidelines:"
        "\n- Provide detailed, informative answers based on the context"
        "\n- If the context doesn't contain enough information, say so clearly"
        "\n- Be conversational and engaging while remaining factual"
        "\n- If asked about technical skills, provide specific examples from the context"
        "\n- If asked about personal details, be respectful and accurate"
        "\n- Connect related information when relevant"
        "\n- Use 3-5 sentences for most answers, but be flexible based on the question"
        "\n- If the question is unclear, ask for clarification"
        "\n\nContext:"
        "\n{context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # Create a chain to combine documents for question answering
    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
    
    # Create a retrieval chain
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)

def get_regular_chat_chain():
    """Create a regular chat chain without RAG context"""
    
    # Simple chat prompt for regular conversations
    chat_system_prompt = (
        "You are a helpful and knowledgeable AI assistant. "
        "Provide informative, accurate, and engaging responses to user questions. "
        "Be conversational, helpful, and professional in your interactions."
    )
    
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", chat_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    return chat_prompt

def process_user_message(
    user_id: str, 
    query: str, 
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a user message and return a response
    
    Args:
        user_id: Unique identifier for the user
        query: User's message/query
        context: Optional collection name for RAG context
    
    Returns:
        dict: Response with answer and metadata
    """
    try:
        # Get user's chat history
        chat_history = get_chat_history(user_id)
        
        # Get current messages from Firebase
        current_messages = chat_history.messages
        
        if context:
            # Use RAG chain with specific context
            rag_chain = get_rag_chain(context)
            result = rag_chain.invoke({
                "input": query, 
                "chat_history": current_messages
            })
            answer = result["answer"]
            response_type = "rag"
        else:
            # Use regular chat without RAG
            chat_chain = get_regular_chat_chain()
            chain = chat_chain | model
            result = chain.invoke({
                "input": query,
                "chat_history": current_messages
            })
            answer = result.content
            response_type = "chat"
        
        # Add messages to Firebase chat history
        chat_history.add_user_message(query)
        chat_history.add_ai_message(str(answer))
        
        return {
            "answer": answer,
            "response_type": response_type,
            "context": context,
            "user_id": user_id,
            "message_count": len(chat_history.messages)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "answer": "I apologize, but I encountered an error processing your request. Please try again.",
            "response_type": "error",
            "context": context,
            "user_id": user_id
        }

def get_user_chat_history(user_id: str, size: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get chat history for a specific user
    
    Args:
        user_id: Unique identifier for the user
        size: Number of messages to return (None for all)
    
    Returns:
        List of message dictionaries
    """
    try:
        chat_history = get_chat_history(user_id)
        messages = chat_history.messages
        
        if size and size > 0:
            messages = messages[-size:]
        
        # Convert messages to dictionary format
        history = []
        for i, message in enumerate(messages):
            history.append({
                "id": i,
                "type": "user" if isinstance(message, HumanMessage) else "ai",
                "content": message.content,
                "timestamp": getattr(message, 'additional_kwargs', {}).get('timestamp', None)
            })
        
        return history
        
    except Exception as e:
        return []

def clear_user_chat_history(user_id: str) -> bool:
    """
    Clear chat history for a specific user
    
    Args:
        user_id: Unique identifier for the user
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        chat_history = get_chat_history(user_id)
        chat_history.clear()
        return True
    except Exception as e:
        return False

def get_available_collections() -> List[str]:
    """Get all available collections from Qdrant"""
    try:
        collections = qdrant_client.get_collections().collections
        return [collection.name for collection in collections]
    except Exception as e:
        return []

# Test function for development
def test_conversational_agent():
    """Test the conversational agent with sample interactions"""
    test_user_id = "test_user_123"
    
    print("🧪 Testing Conversational Agent")
    print("=" * 40)
    
    # Test regular chat
    print("\n📝 Testing regular chat (no context):")
    result = process_user_message(test_user_id, "Hello! How are you today?")
    print(f"Response: {result['answer']}")
    
    # Test RAG chat with context
    collections = get_available_collections()
    if collections:
        context = collections[0]
        print(f"\n📝 Testing RAG chat with context '{context}':")
        result = process_user_message(
            test_user_id, 
            "Tell me about this collection", 
            context=context
        )
        print(f"Response: {result['answer']}")
    
    # Test chat history
    print(f"\n📚 Chat history for user {test_user_id}:")
    history = get_user_chat_history(test_user_id)
    for msg in history:
        print(f"  {msg['type'].upper()}: {msg['content'][:50]}...")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    test_conversational_agent() 