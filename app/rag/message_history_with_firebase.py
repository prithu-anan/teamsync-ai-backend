from dotenv import load_dotenv
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_test import model

# Load credentials from .env
load_dotenv()

# Firebase/Firestore setup
PROJECT_ID = "langchain-demo-6d982"  # Your actual project ID
SESSION_ID = "user_session_new"
COLLECTION_NAME = "chat_history"

print("Initializing Firestore client...")
client = firestore.Client(project=PROJECT_ID)

print("Setting up chat history...")
chat_history = FirestoreChatMessageHistory(
    session_id=SESSION_ID,
    collection=COLLECTION_NAME,
    client=client,
)

print("Ready to chat! Type 'exit' to quit.")

while True:
    human_input = input("User: ")
    if human_input.lower() == "exit":
        break

    chat_history.add_user_message(human_input)

    ai_response = model.invoke(chat_history.messages)
    chat_history.add_ai_message(str(ai_response.content))

    print(f"AI: {ai_response.content}")
