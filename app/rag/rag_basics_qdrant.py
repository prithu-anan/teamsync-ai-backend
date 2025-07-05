import os
import time
import logging
from typing import List, Optional
from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Qdrant
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from quadrant_client import qdrant_client

# ==== Config ====
COLLECTION_NAME = "suhas_profile_chunks"
BATCH_SIZE = 5  # Reduced from 20 to 5 for better timeout handling
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

def main():
    """Main function to handle document processing and upload"""
    try:
        # ==== Load file ====
        logger.info("Loading documents...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "books", "myself.txt")
        
        loader = TextLoader(file_path)
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} document(s)")

        # ==== Token-based text splitting with cl100k_base encoding ====
        logger.info("Splitting documents into chunks...")
        text_splitter = TokenTextSplitter(
            chunk_size=500,  # Reduced from 750 to 500 for smaller chunks
            chunk_overlap=100,  # Reduced from 150 to 100
            encoding_name="cl100k_base"
        )
        docs = text_splitter.split_documents(documents)
        logger.info(f"Created {len(docs)} chunks")

        # ==== Embeddings ====
        logger.info("Initializing embeddings model...")
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            timeout=TIMEOUT
        )
        vector_size = len(embeddings.embed_query("test"))
        logger.info(f"Vector size: {vector_size}")

        # ==== Clear and recreate collection ====
        clear_collection_if_exists(COLLECTION_NAME)
        
        logger.info("Creating collection...")
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info(f"Collection '{COLLECTION_NAME}' created successfully")

        # ==== Connect vector store ====
        qdrant_store = Qdrant(
            client=qdrant_client,
            collection_name=COLLECTION_NAME,
            embeddings=embeddings,
        )

        # ==== Upload documents in small batches with retry logic ====
        logger.info(f"🚀 Starting upload of {len(docs)} chunks in batches of {BATCH_SIZE}...")
        
        successful_uploads = 0
        failed_uploads = 0
        
        for i in range(0, len(docs), BATCH_SIZE):
            batch = docs[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (len(docs) + BATCH_SIZE - 1) // BATCH_SIZE
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)")
            
            if upload_batch_with_retry(batch, qdrant_store, embeddings, batch_num):
                successful_uploads += len(batch)
            else:
                failed_uploads += len(batch)
                logger.error(f"Failed to upload batch {batch_num}")
            
            # Add delay between batches to prevent overwhelming the server
            if i + BATCH_SIZE < len(docs):
                time.sleep(0.5)

        # ==== Summary ====
        logger.info("=" * 50)
        logger.info("📊 UPLOAD SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total chunks: {len(docs)}")
        logger.info(f"Successfully uploaded: {successful_uploads}")
        logger.info(f"Failed uploads: {failed_uploads}")
        logger.info(f"Success rate: {(successful_uploads/len(docs)*100):.1f}%")
        
        if failed_uploads == 0:
            logger.info("🎉 All documents uploaded to Qdrant successfully!")
        else:
            logger.warning(f"⚠️ {failed_uploads} chunks failed to upload. Consider re-running the script.")
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
