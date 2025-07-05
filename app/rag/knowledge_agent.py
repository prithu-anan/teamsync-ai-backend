"""
Knowledge Agent for RAG System

This module provides functionality to manage knowledge collections in Qdrant.
It can add documents to existing collections and create new collections from folders.
"""

import os
import time
import logging
import shutil
from typing import List, Optional
from pathlib import Path
from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import Qdrant
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
from langchain_core.documents import Document

try:
    from app.rag.quadrant_client import qdrant_client
    from app.rag.embedding_model import embedding_model
except ImportError:
    # Fallback for direct script execution
    from quadrant_client import qdrant_client
    from embedding_model import embedding_model

# ==== Config ====
BATCH_SIZE = 5
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
TIMEOUT = 30  # seconds

# ==== Setup logging ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_embeddings_batch(texts: List[str], embeddings_model, max_retries: int = 3) -> List[List[float]]:
    """Create embeddings for a batch of texts with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Creating embeddings for batch of {len(texts)} texts (attempt {attempt + 1})")
            return embeddings_model.embed_documents(texts)
        except Exception as e:
            logger.warning(f"Embedding attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(RETRY_DELAY)
    return []

def upload_batch_with_retry(batch: List[Document], qdrant_store, embeddings_model, batch_num: int) -> bool:
    """Upload a batch of documents with retry logic and timeout handling"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Uploading batch {batch_num} (attempt {attempt + 1})")
            
            # Create embeddings first
            texts = [doc.page_content for doc in batch]
            embeddings = create_embeddings_batch(texts, embeddings_model)
            
            # Upload to Qdrant with timeout
            start_time = time.time()
            qdrant_store.add_documents(batch)
            upload_time = time.time() - start_time
            
            logger.info(f"✅ Successfully uploaded batch {batch_num} in {upload_time:.2f}s")
            return True
            
        except UnexpectedResponse as e:
            logger.error(f"Qdrant error in batch {batch_num} (attempt {attempt + 1}): {str(e)}")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to upload batch {batch_num} after {MAX_RETRIES} attempts")
                return False
            time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Unexpected error in batch {batch_num} (attempt {attempt + 1}): {str(e)}")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to upload batch {batch_num} after {MAX_RETRIES} attempts")
                return False
            time.sleep(RETRY_DELAY)
    
    return False

def clear_collection_if_exists(collection_name: str):
    """Clear existing collection to start fresh"""
    try:
        existing_collections = qdrant_client.get_collections().collections
        if collection_name in [c.name for c in existing_collections]:
            logger.info(f"Clearing existing collection: {collection_name}")
            qdrant_client.delete_collection(collection_name)
            time.sleep(1)  # Wait for deletion to complete
    except Exception as e:
        logger.warning(f"Could not clear collection: {str(e)}")

def load_document(file_path: str) -> List[Document]:
    """Load document from file path, supporting .txt and .md files"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")
    
    if path.suffix.lower() == '.txt':
        loader = TextLoader(str(path))
    elif path.suffix.lower() == '.md':
        loader = UnstructuredMarkdownLoader(str(path))
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}. Supported: .txt, .md")
    
    return loader.load()

def split_documents(documents: List[Document], chunk_size: int = 500, chunk_overlap: int = 100) -> List[Document]:
    """Split documents into chunks using token-based splitting"""
    logger.info("Splitting documents into chunks...")
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        encoding_name="cl100k_base"
    )
    docs = text_splitter.split_documents(documents)
    logger.info(f"Created {len(docs)} chunks")
    return docs

def create_collection(collection_name: str, vector_size: int):
    """Create a new collection in Qdrant"""
    clear_collection_if_exists(collection_name)
    
    logger.info("Creating collection...")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    logger.info(f"Collection '{collection_name}' created successfully")

def get_qdrant_store(collection_name: str):
    """Get Qdrant vector store for a collection"""
    return Qdrant(
        client=qdrant_client,
        collection_name=collection_name,
        embeddings=embedding_model,
    )

def upload_documents_to_collection(documents: List[Document], collection_name: str) -> dict:
    """Upload documents to a collection with progress tracking"""
    logger.info(f"🚀 Starting upload of {len(documents)} chunks to collection '{collection_name}'...")
    
    # Get vector size
    vector_size = len(embedding_model.embed_query("test"))
    
    # Create collection if it doesn't exist
    try:
        existing_collections = qdrant_client.get_collections().collections
        if collection_name not in [c.name for c in existing_collections]:
            create_collection(collection_name, vector_size)
    except Exception as e:
        logger.error(f"Failed to create collection: {str(e)}")
        raise
    
    # Get Qdrant store
    qdrant_store = get_qdrant_store(collection_name)
    
    # Upload documents in batches
    successful_uploads = 0
    failed_uploads = 0
    
    for i in range(0, len(documents), BATCH_SIZE):
        batch = documents[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)")
        
        if upload_batch_with_retry(batch, qdrant_store, embedding_model, batch_num):
            successful_uploads += len(batch)
        else:
            failed_uploads += len(batch)
            logger.error(f"Failed to upload batch {batch_num}")
        
        # Add delay between batches to prevent overwhelming the server
        if i + BATCH_SIZE < len(documents):
            time.sleep(0.5)
    
    return {
        "total": len(documents),
        "successful": successful_uploads,
        "failed": failed_uploads,
        "success_rate": (successful_uploads/len(documents)*100) if documents else 0
    }

def add_document_to_collection(collection_name: str, document_path: str) -> dict:
    """
    Add a single document to an existing collection
    
    Args:
        collection_name: Name of the collection to add document to
        document_path: Path to the document file
    
    Returns:
        dict: Upload statistics
    """
    try:
        # Load document
        documents = load_document(document_path)
        
        # Split into chunks
        chunks = split_documents(documents)
        
        # Upload to collection
        result = upload_documents_to_collection(chunks, collection_name)
        
        logger.info(f"✅ Document '{document_path}' added to collection '{collection_name}'")
        return result
        
    except Exception as e:
        logger.error(f"Failed to add document to collection: {str(e)}")
        raise

def add_collection(collection_folder_path: str) -> dict:
    """
    Create a new collection from a folder of documents
    
    Args:
        collection_folder_path: Path to the folder containing documents
    
    Returns:
        dict: Upload statistics
    """
    try:
        collection_folder = Path(collection_folder_path)
        
        if not collection_folder.exists():
            raise FileNotFoundError(f"Collection folder not found: {collection_folder_path}")
        
        # Extract collection name from folder name
        collection_name = collection_folder.name
        
        # Move folder to books directory if it's not already there
        books_dir = Path(__file__).parent / "books"
        target_folder = books_dir / collection_name
        
        if collection_folder != target_folder:
            if target_folder.exists():
                logger.warning(f"Collection folder '{collection_name}' already exists in books directory")
            else:
                logger.info(f"Moving collection folder to books directory: {target_folder}")
                shutil.copytree(collection_folder, target_folder)
                collection_folder = target_folder
        
        # Load all documents from the folder
        documents = []
        supported_extensions = {'.txt', '.md'}
        
        for file_path in collection_folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    file_docs = load_document(str(file_path))
                    documents.extend(file_docs)
                    logger.info(f"Loaded document: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to load document {file_path}: {str(e)}")
        
        if not documents:
            raise ValueError(f"No supported documents found in folder: {collection_folder_path}")
        
        # Split documents into chunks
        chunks = split_documents(documents)
        
        # Upload to collection
        result = upload_documents_to_collection(chunks, collection_name)
        
        logger.info(f"✅ Collection '{collection_name}' created with {len(documents)} documents")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create collection: {str(e)}")
        raise

def get_all_collections() -> List[str]:
    """Get all existing collection names from Qdrant"""
    try:
        collections = qdrant_client.get_collections().collections
        return [collection.name for collection in collections]
    except Exception as e:
        logger.error(f"Failed to get collections: {str(e)}")
        return []

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python knowledge_agent.py <command> [args...]")
        print("Commands:")
        print("  add-doc <collection_name> <document_path>")
        print("  add-collection <folder_path>")
        print("  list-collections")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "add-doc":
            if len(sys.argv) != 4:
                print("Usage: python knowledge_agent.py add-doc <collection_name> <document_path>")
                sys.exit(1)
            
            collection_name = sys.argv[2]
            document_path = sys.argv[3]
            result = add_document_to_collection(collection_name, document_path)
            print(f"✅ Document added successfully: {result}")
            
        elif command == "add-collection":
            if len(sys.argv) != 3:
                print("Usage: python knowledge_agent.py add-collection <folder_path>")
                sys.exit(1)
            
            folder_path = sys.argv[2]
            result = add_collection(folder_path)
            print(f"✅ Collection created successfully: {result}")
            
        elif command == "list-collections":
            collections = get_all_collections()
            print("📚 Available collections:")
            for collection in collections:
                print(f"  - {collection}")
                
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1) 