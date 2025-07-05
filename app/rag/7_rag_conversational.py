import os

from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Qdrant
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from quadrant_client import qdrant_client  # ✅ Your custom Qdrant setup
from langchain_test import model as llm

# Load environment variables from .env
load_dotenv()

# === Config ===
COLLECTION_NAME = "suhas_profile_chunks"

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


# Enhanced function to simulate a continual chat with better message handling
def continual_chat():
    print("🤖 Welcome to the AI Assistant! I have information about Suhas Abdullah and Prithu Anan.")
    print("💡 You can ask me about their backgrounds, projects, skills, or any related topics.")
    print("📝 Type 'exit' to end the conversation.")
    print("=" * 60)
    
    chat_history = []  # Collect chat history here (a sequence of messages)
    
    while True:
        try:
            query = input("\n👤 You: ").strip()
            
            if query.lower() == "exit":
                print("\n👋 Goodbye! Thanks for chatting!")
                break
                
            if not query:
                print("🤔 Please enter a question or type 'exit' to leave.")
                continue
            
            # Process the user's query through the retrieval chain
            result = rag_chain.invoke({"input": query, "chat_history": chat_history})
            
            # Display the AI's response
            print(f"\n🤖 AI: {result['answer']}")
            
            # Update the chat history with proper message types
            chat_history.append(HumanMessage(content=query))
            chat_history.append(AIMessage(content=result["answer"]))
            
            # Keep chat history manageable (limit to last 10 exchanges)
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]
                
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
    print("=" * 50)
    
    chat_history = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        try:
            result = rag_chain.invoke({"input": question, "chat_history": chat_history})
            print(f"✅ Response: {result['answer'][:100]}...")
            chat_history.append(HumanMessage(content=question))
            chat_history.append(AIMessage(content=result["answer"]))
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Testing completed!")


# Main function to start the continual chat
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_system()
    else:
        continual_chat()
