import os
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings  # ✅ Updated import for OpenAI embeddings
from quadrant_client import qdrant_client  # ✅ Your custom Qdrant setup

# === Config ===
COLLECTION_NAME = "suhas_profile_chunks"

# === Embeddings ===
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # ✅ Updated to OpenAI embeddings

# === Load Qdrant vector store ===
qdrant_store = Qdrant(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings,
)

# === Prepare retriever ===
retriever = qdrant_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.5},
)

# === User query loop ===
print("\nAsk something about Suhas (Ctrl+C to exit)\n")

try:
    while True:
        query = input("🔍 Your question: ").strip()
        if not query:
            continue

        results = retriever.invoke(query)

        if not results:
            print("❌ No relevant documents found.\n")
            continue

        print("\n--- 📚 Relevant Chunks ---")
        for i, doc in enumerate(results, 1):
            print(f"\n📄 Chunk {i}:\n{doc.page_content.strip()}")
            if doc.metadata:
                print(f"🔗 Source: {doc.metadata.get('source', 'Unknown')}")
        print()

except KeyboardInterrupt:
    print("\n👋 Exiting. Goodbye!")
