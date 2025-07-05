"""
Conversational RAG System with Firebase Chat History

This module implements a conversational RAG (Retrieval-Augmented Generation) system
that uses Firebase Firestore to persist chat history across sessions.

Features:
- Persistent chat history using Firebase Firestore
- History-aware question reformulation
- Context-aware responses based on retrieved documents
- Session management with unique session IDs

Usage:
- python 7_rag_conversational.py          # Start interactive chat
- python 7_rag_conversational.py --test   # Run test questions
- python 7_rag_conversational.py --clear  # Clear chat history

Dependencies:
- Firebase/Firestore for chat history persistence
- Qdrant for vector storage
- OpenAI for embeddings and LLM
"""

import os

from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Qdrant
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory

from quadrant_client import qdrant_client  # ✅ Your custom Qdrant setup
from langchain_test import model as llm

# Load environment variables from .env
load_dotenv()

# === Config ===
COLLECTION_NAME = "suhas_profile_chunks"

# === Firebase/Firestore setup ===
PROJECT_ID = "langchain-demo-6d982"  # Your actual project ID
SESSION_ID = "rag_conversational_session"
CHAT_HISTORY_COLLECTION = "rag_chat_history"

# Initialize Firestore client
print("Initializing Firestore client...")
firestore_client = firestore.Client(project=PROJECT_ID)

# Setup Firebase chat history
print("Setting up Firebase chat history...")
firebase_chat_history = FirestoreChatMessageHistory(
    session_id=SESSION_ID,
    collection=CHAT_HISTORY_COLLECTION,
    client=firestore_client,
)

# Define the embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Load the existing Qdrant vector store
qdrant_store = Qdrant(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings,
)

# Create a retriever for querying the vector store
# Using similarity_score_threshold for better control over retrieval quality
retriever = qdrant_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},  # Increased from 3 to 5 for better context
)


# Enhanced contextualize question prompt
# This system prompt helps the AI understand that it should reformulate the question
# based on the chat history to make it a standalone question
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

# Create a prompt template for contextualizing questions
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Create a history-aware retriever
# This uses the LLM to help reformulate the question based on chat history
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Enhanced answer question prompt
# This system prompt helps the AI understand that it should provide comprehensive answers
# based on the retrieved context and indicates what to do if the answer is unknown
qa_system_prompt = (
    "You are a knowledgeable assistant with access to detailed information about Suhas Abdullah and Prithu Anan. "
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

# Create a prompt template for answering questions
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Create a chain to combine documents for question answering
# `create_stuff_documents_chain` feeds all retrieved context into the LLM
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Create a retrieval chain that combines the history-aware retriever and the question answering chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


# Enhanced function to simulate a continual chat with Firebase persistence
def continual_chat():
    print("🤖 Welcome to the AI Assistant!")
    print("📝 Type 'exit' to end the conversation.")
    print("💾 Chat history will be persisted in Firebase.")
    print("=" * 60)
    
    # Load existing chat history from Firebase
    existing_messages = firebase_chat_history.messages
    if existing_messages:
        print(f"📚 Loaded {len(existing_messages)} previous messages from Firebase.")
    
    while True:
        try:
            query = input("\n👤 You: ").strip()
            
            if query.lower() == "exit":
                print("\n👋 Goodbye! Thanks for chatting!")
                break
                
            if not query:
                print("🤔 Please enter a question or type 'exit' to leave.")
                continue
            
            # Get current chat history from Firebase
            chat_history = firebase_chat_history.messages
            
            # Process the user's query through the retrieval chain
            result = rag_chain.invoke({"input": query, "chat_history": chat_history})
            
            # Display the AI's response
            print(f"\n🤖 AI: {result['answer']}")
            
            # Add messages to Firebase chat history
            firebase_chat_history.add_user_message(query)
            firebase_chat_history.add_ai_message(result["answer"])
            
            # Keep chat history manageable (limit to last 20 exchanges = 40 messages)
            current_messages = firebase_chat_history.messages
            if len(current_messages) > 40:
                # Note: Firebase doesn't have a direct way to trim history
                # The history will grow, but you can implement cleanup logic if needed
                print(f"📊 Chat history now has {len(current_messages)} messages.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("🔄 Please try again with a different question.")


# Function to test the system with sample questions
def test_system():
    """Test the RAG system with sample questions to verify functionality"""
    test_questions = [
        "Who is Suhas Abdullah?",
        "What projects has Prithu worked on?",
        "What are Suhas's technical skills?",
        "Tell me about Prithu's academic background",
        "What is Greenblox?",
        "What competitions has Prithu participated in?"
    ]
    
    print("🧪 Testing RAG System with Sample Questions")
    print("💾 Test results will be saved to Firebase.")
    print("=" * 50)
    
    # Use Firebase chat history for testing
    chat_history = firebase_chat_history.messages
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        try:
            result = rag_chain.invoke({"input": question, "chat_history": chat_history})
            print(f"✅ Response: {result['answer'][:100]}...")
            
            # Add to Firebase chat history
            firebase_chat_history.add_user_message(question)
            firebase_chat_history.add_ai_message(result["answer"])
            
            # Update chat_history for next iteration
            chat_history = firebase_chat_history.messages
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Testing completed!")
    print(f"📊 Total messages in Firebase: {len(firebase_chat_history.messages)}")


# Function to clear chat history
def clear_chat_history():
    """Clear all chat history from Firebase"""
    try:
        # Clear all messages from Firebase
        firebase_chat_history.clear()
        print("🗑️ Chat history cleared successfully!")
    except Exception as e:
        print(f"❌ Error clearing chat history: {str(e)}")

# Main function to start the continual chat
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_system()
        elif sys.argv[1] == "--clear":
            clear_chat_history()
        else:
            print("Usage: python 7_rag_conversational.py [--test|--clear]")
    else:
        continual_chat()
