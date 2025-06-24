from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, task , channel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # <-- Allow all methods: GET, POST, etc.
    allow_headers=["*"],  # <-- Allow all headers
)
app.include_router(health.router)
app.include_router(task.router)
app.include_router(channel.router)
