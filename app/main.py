from fastapi import FastAPI
from app.routes import health, task, channel, chatbot
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TeamSync AI Backend",
    description="Backend API for TeamSync AI with RAG-powered chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(health.router)
app.include_router(task.router)
app.include_router(channel.router)
app.include_router(chatbot.router)
