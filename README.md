## Project Setup

* Clone the repository

```bash
git clone https://github.com/suhashines/teamysnc-ai-backend.git
cd teamysnc-ai-backend
```

* Create and activate virtual environment

```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
```

* Install the dependencies

```bash
pip install -r requirements.txt
```

* Create a .env file with the following credential - 

```bash
DATABASE_URL=YOUR_DATABASE_URL
GEMINI_API_KEY=GEMINI_API_KEY
GOOGLE_APPLICATION_CREDENTIALS=FIREBASE_CREDENTIALS
QUADRANT_URL=VECTOR_STORE_URL
QUADRANT_API_KEY=YOUR_QUADRANT_API_KEY
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
PROJECT_ID=FIREBASE_PROJECT_ID
BASE_SERVER_URL=BACKEND_SERVER_URL
```

* Make sure the postgres docker service is running
* Then run fast api backend

```bash
uvicorn app.main:app --reload
```

- Health check 

[Click on this link]( http://localhost:8000/health)

- You'll see

```javascript
{
  "status": "healthy",
  "message": "Connected to database",
  "time": "2025-06-09T14:43:26.135516+00:00"
}
```

### Add Knowledgebase to RAG

The RAG system allows you to manage knowledge collections and documents. Here's how to use it:

#### Directory Structure
```
app/rag/
├── books/                    # Collection folders
│   ├── about_us/            # Collection: about_us
│   │   ├── document1.txt    # Documents (.txt, .md)
│   │   └── document2.md
│   └── code_pilot/          # Collection: code_pilot
│       ├── guide.txt
│       └── examples.md
├── knowledge_agent.py        # Knowledge management script
├── conversational_agent.py   # Chat functionality
└── ...
```

#### 1. Adding Documents to Existing Collection

```bash
# From project root
python app/rag/knowledge_agent.py add-doc <collection_name> <document_path>

# Example: Add a document to 'about_us' collection
python app/rag/knowledge_agent.py add-doc about_us /path/to/new_document.txt
```

#### 2. Creating New Collections

**Option A: From existing folder**
```bash
# Create collection from folder (will be moved to books/)
python app/rag/knowledge_agent.py add-collection /path/to/your/folder

# Example: Create collection from existing about_us folder
python app/rag/knowledge_agent.py add-collection app/rag/books/about_us
```

**Option B: Create folder structure manually**
1. Create a new folder in `app/rag/books/` (e.g., `app/rag/books/my_collection/`)
2. Add your documents (`.txt` or `.md` files) to the folder
3. Run the add-collection command:
```bash
python app/rag/knowledge_agent.py add-collection app/rag/books/my_collection
```

#### 3. List Available Collections

```bash
python app/rag/knowledge_agent.py list-collections
```

#### 4. Supported File Types
- `.txt` files (plain text)
- `.md` files (Markdown)

#### 5. Collection Management Commands

```bash
# List all collections
python app/rag/knowledge_agent.py list-collections

# Add document to existing collection
python app/rag/knowledge_agent.py add-doc <collection_name> <document_path>

# Create new collection from folder
python app/rag/knowledge_agent.py add-collection <folder_path>
```

#### Example Workflow

1. **Create a new collection:**
```bash
# Create folder structure
mkdir -p app/rag/books/company_docs
# Add documents to the folder
echo "Company information..." > app/rag/books/company_docs/company.txt
# Create collection
python app/rag/knowledge_agent.py add-collection app/rag/books/company_docs
```

2. **Add more documents later:**
```bash
python app/rag/knowledge_agent.py add-doc company_docs /path/to/new_document.txt
```

3. **Verify collections:**
```bash
python app/rag/knowledge_agent.py list-collections
```

#### Notes
- Collections are automatically created in Qdrant if they don't exist
- Documents are split into chunks for better retrieval
- Upload progress and statistics are shown during processing
- Collections can be used as context in the chatbot API

### Chatbot API with Agent Integration

The chatbot now supports three modes:

#### 1. **RAG Mode** (with context)
- Use when `context` parameter is provided
- Retrieves information from specific collections
- Example: `{"query": "Tell me about Suhas", "context": "about_us"}`

#### 2. **Agent Mode** (personalized, no context)
- Use when no `context` is provided but JWT token is present
- Uses LangChain agents with tools to access backend API
- Can fetch user information, tasks, and other personalized data
- Example: `{"query": "What are my tasks?", "context": null}` with JWT header

#### 3. **Regular Chat Mode** (fallback)
- Use when no context and no JWT token
- Simple conversational responses

#### Environment Variables
```bash
# Add to your .env file
BASE_SERVER_URL=http://localhost:8080  # Backend server URL
```

#### API Usage Examples

**RAG Query:**
```bash
curl -X POST "http://localhost:8000/chatbot/user123" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about the company", "context": "about_us"}'
```

**Agent Query (Personalized):**
```bash
curl -X POST "http://localhost:8000/chatbot/user123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "What are my current tasks?", "context": null}'
```

**Regular Chat:**
```bash
curl -X POST "http://localhost:8000/chatbot/user123" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello! How are you?", "context": null}'
```



